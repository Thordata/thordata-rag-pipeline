"""Specialized ingestor using Thordata's Web Scraper API with smart routing."""
from __future__ import annotations

import json
import logging
import time
from typing import Any, Dict, Optional
from urllib.parse import parse_qs, urlparse

import requests
from thordata import AsyncThordataClient

from ..core.config import settings
from .registry import SPIDER_REGISTRY, SpiderConfig
from .spider_discovery import SpiderDiscovery

logger = logging.getLogger(__name__)


class SpecializedIngestor:
    """Specialized ingestor that routes URLs to appropriate Thordata spiders."""

    def __init__(
        self,
        scraper_token: Optional[str] = None,
        public_token: Optional[str] = None,
        public_key: Optional[str] = None,
        use_auto_discovery: bool = True,
    ):
        """Initialize the specialized ingestor.

        Args:
            scraper_token: Optional scraper token. If not provided, uses settings.
            public_token: Optional public token. If not provided, uses settings.
            public_key: Optional public key. If not provided, uses settings.
            use_auto_discovery: Whether to use automatic spider discovery from SDK.
        """
        self.scraper_token = scraper_token or settings.THORDATA_SCRAPER_TOKEN
        self.public_token = public_token or settings.THORDATA_PUBLIC_TOKEN
        self.public_key = public_key or settings.THORDATA_PUBLIC_KEY
        self.discovery = SpiderDiscovery() if use_auto_discovery else None

    async def _create_video_task(
        self, cfg: SpiderConfig, final_params: Dict[str, Any]
    ) -> str:
        """Create a video task using SDK's create_scraper_task with universal params.

        Args:
            cfg: Spider configuration
            final_params: Final parameters for the task

        Returns:
            Task ID string
        """
        # Prepare universal settings for video tasks
        universal_params = {
            "resolution": "<=360p",
            "video_codec": "vp9",
            "audio_format": "opus",
            "bitrate": "<=320",
            "selected_only": "false",
        }

        async with AsyncThordataClient(
            scraper_token=self.scraper_token,
            public_token=self.public_token,
            public_key=self.public_key,
        ) as client:
            try:
                # Use create_scraper_task with universal_params for video tasks
                task_id = await client.create_scraper_task(
                    file_name=f"rag_vid_{cfg.id}",
                    spider_id=cfg.id,
                    spider_name=cfg.name,
                    parameters=final_params,
                    universal_params=universal_params,
                )
                return task_id
            except Exception as e:
                # Fallback to raw API if SDK method fails
                logger.warning(f"create_scraper_task failed, using raw API for {cfg.id}: {e}")
                return await self._create_video_task_raw(cfg, final_params)

    async def _create_video_task_raw(
        self, cfg: SpiderConfig, final_params: Dict[str, Any]
    ) -> str:
        """Create a video task using raw API (fallback method).

        Args:
            cfg: Spider configuration
            final_params: Final parameters for the task

        Returns:
            Task ID string
        """
        import aiohttp

        spider_universal = {
            "resolution": "<=360p",
            "video_codec": "vp9",
            "audio_format": "opus",
            "bitrate": "<=320",
            "selected_only": "false",
        }

        payload = {
            "file_name": f"rag_vid_{cfg.id}",
            "spider_id": cfg.id,
            "spider_name": cfg.name,
            "spider_parameters": json.dumps([final_params]),
            "spider_errors": "true",
            "spider_universal": json.dumps(spider_universal),
        }

        from thordata._utils import build_builder_headers

        headers = build_builder_headers(
            self.scraper_token or "",
            self.public_token or "",
            self.public_key or "",
        )

        video_builder_url = "https://scraperapi.thordata.com/video_builder"

        async with aiohttp.ClientSession() as session:
            async with session.post(video_builder_url, data=payload, headers=headers) as resp:
                resp.raise_for_status()
                data = await resp.json()

                if data.get("code") != 200:
                    raise Exception(f"Video Builder API Error: {data}")

                return data["data"]["task_id"]

    async def _run_spider(
        self,
        config_key: str,
        input_value: str,
        dynamic_params: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """Run a spider task and wait for results.

        Args:
            config_key: Registry key for the spider
            input_value: Main input value (URL, keyword, etc.)
            dynamic_params: Optional additional parameters

        Returns:
            JSON string of results, or None if failed
        """
        # Use merged registry if auto-discovery is enabled
        if self.discovery:
            registry = self.discovery.get_merged_registry()
        else:
            registry = SPIDER_REGISTRY

        cfg = registry.get(config_key)
        if not cfg:
            logger.error(f"Registry key not found: {config_key}")
            # Try to find by spider_id directly
            if self.discovery:
                for key, config in registry.items():
                    if config.id == config_key:
                        cfg = config
                        logger.info(f"Found spider by ID: {config_key} -> {key}")
                        break
            if not cfg:
                return None

        final_params = {cfg.input_key: input_value}
        if cfg.extra_params:
            final_params.update(cfg.extra_params)
        if dynamic_params:
            final_params.update(dynamic_params)

        logger.info(f"Using spider: {cfg.desc} ({cfg.id})")

        try:
            task_id = ""

            async with AsyncThordataClient(
                scraper_token=self.scraper_token,
                public_token=self.public_token,
                public_key=self.public_key,
            ) as client:
                if cfg.is_video:
                    # Use raw API for video tasks
                    task_id = await self._create_video_task(cfg, final_params)
                else:
                    # Use SDK for standard data tasks
                    task_id = await client.create_scraper_task(
                        file_name=f"rag_{cfg.id}",
                        spider_id=cfg.id,
                        spider_name=cfg.name,
                        parameters=final_params,
                    )

                logger.info(f"Task {task_id} created. Polling...")

                # Wait for task completion
                status = await client.wait_for_task(
                    task_id,
                    poll_interval=3.0,
                    max_wait=settings.SCRAPING_TIMEOUT,
                )

                if status.lower() not in ["ready", "success", "finished"]:
                    error_msg = f"Task {task_id} ended with status: {status}"
                    logger.error(error_msg)
                    # Try to get error details if available
                    try:
                        task_info = await client.get_task_status(task_id)
                        if isinstance(task_info, dict) and "error" in task_info:
                            error_msg += f" - {task_info['error']}"
                    except Exception:
                        pass
                    raise Exception(error_msg)

                # Get download URL
                download_url = await client.get_task_result(task_id, file_type="json")

                # Download and parse
                logger.info("Downloading data...")
                resp = requests.get(download_url, timeout=60)

                try:
                    data = resp.json()
                except Exception:
                    return resp.text

                if isinstance(data, list):
                    if not data:
                        return None
                    if len(data) == 1:
                        return json.dumps(data[0], indent=2, ensure_ascii=False)

                return json.dumps(data, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            return None

    async def route_and_scrape(self, url: str) -> Optional[str]:
        """Route URL to appropriate spider and scrape.

        Args:
            url: Target URL to scrape

        Returns:
            JSON string of results, or None if no route found
        """
        # Try auto-discovery first if enabled
        if self.discovery:
            spider_key = self.discovery.find_spider_by_url(url)
            if spider_key:
                logger.info(f"Auto-discovered spider: {spider_key} for {url}")
                # Extract input value based on spider config
                registry = self.discovery.get_merged_registry()
                cfg = registry.get(spider_key)
                if cfg:
                    if cfg.input_key == "url":
                        return await self._run_spider(spider_key, url)
                    # For other input keys, try to extract from URL
                    parsed = urlparse(url)
                    query = parse_qs(parsed.query)
                    if cfg.input_key in query:
                        return await self._run_spider(spider_key, query[cfg.input_key][0])
                    # Fallback to URL
                    return await self._run_spider(spider_key, url)

        # Fallback to manual routing
        parsed = urlparse(url)
        path = parsed.path
        query = parse_qs(parsed.query)
        domain = parsed.netloc.lower()

        # Amazon routing
        if "amazon" in domain:
            if "/s" in url and "k" in query:
                return await self._run_spider(
                    "amazon_search",
                    query["k"][0],
                    {"domain": f"{parsed.scheme}://{parsed.netloc}/"},
                )
            if "product-reviews" in url:
                return await self._run_spider("amazon_review", url)
            if "seller=" in url or "/sp?" in url:
                return await self._run_spider("amazon_seller", url)
            return await self._run_spider("amazon_product", url, {"country": "us"})

        # Google Maps routing
        elif "google.com/maps" in url:
            if "reviews" in url:
                return await self._run_spider("gmaps_review", url)
            return await self._run_spider("gmaps_detail", url)

        # YouTube routing
        elif "youtube.com" in domain or "youtu.be" in domain:
            if "v=" in url or "youtu.be" in domain:
                return await self._run_spider("youtube_video", url)
            elif "@" in path or "/channel/" in path:
                return await self._run_spider("youtube_channel", url)

        # TikTok routing
        elif "tiktok.com" in domain:
            if "/video/" in path:
                return await self._run_spider("tiktok_post", url)
            if "@" in path:
                return await self._run_spider("tiktok_profile", url)
            if "shop" in path:
                return await self._run_spider("tiktok_shop", url)
            return await self._run_spider("tiktok_comment", url)

        # Google Play routing
        elif "play.google.com" in domain:
            return await self._run_spider("play_store_app", url)

        # Instagram routing
        elif "instagram.com" in domain:
            if "/reel/" in path:
                return await self._run_spider("ins_reel", url)
            if "/p/" in path:
                return await self._run_spider("ins_comment", url)
            parts = [p for p in path.split("/") if p]
            if len(parts) == 1 and parts[0] not in ("explore", "direct"):
                return await self._run_spider("ins_profile", parts[0])
            return await self._run_spider("ins_post", url)

        # Facebook routing
        elif "facebook.com" in domain:
            if "/search" in path and "q" in query:
                return await self._run_spider("facebook_search", query["q"][0])
            return await self._run_spider("facebook_post", url)

        # Twitter/X routing
        elif "twitter.com" in domain or "x.com" in domain:
            if "/status/" in path:
                return await self._run_spider("twitter_post", url)
            return await self._run_spider("twitter_profile", url)

        # LinkedIn routing
        elif "linkedin.com" in domain:
            if "/jobs/" in path:
                return await self._run_spider("linkedin_job", url)
            return await self._run_spider("linkedin_company", url)

        # Reddit routing
        elif "reddit.com" in domain:
            if "/comments/" in path:
                return await self._run_spider("reddit_comment", url)
            return await self._run_spider("reddit_post", url)

        # GitHub routing
        elif "github.com" in domain:
            return await self._run_spider("github_repo", url)

        return None
