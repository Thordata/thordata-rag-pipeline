import requests
import json
import time
from typing import Optional, Dict, Any
from urllib.parse import urlparse, parse_qs
from thordata import ThordataClient
from .registry import SPIDER_REGISTRY

class SpecializedIngestor:
    def __init__(self, scraper_token: str, public_token: Optional[str] = None, public_key: Optional[str] = None):
        self.client = ThordataClient(
            scraper_token=scraper_token,
            public_token=public_token,
            public_key=public_key
        )

    def _create_video_task_raw(self, cfg, final_params) -> str:
        """
        Manually create video task to bypass SDK CommonSettings limitations.
        Matches the successful Python/CURL example EXACTLY.
        """
        # 1. Payload Values (Clean, no windows escaping)
        spider_universal = {
            "resolution": "<=360p", 
            "video_codec": "vp9",
            "audio_format": "opus",
            "bitrate": "<=320",
            "selected_only": "false"
        }
        
        payload = {
            "file_name": f"rag_vid_{cfg.id}",
            "spider_id": cfg.id,
            "spider_name": cfg.name,
            "spider_parameters": json.dumps([final_params]),
            "spider_errors": "true",
            # CRITICAL FIX: Use 'spider_universal' instead of 'common_settings'
            # to match the raw API expectation / working CURL example.
            "spider_universal": json.dumps(spider_universal) 
        }

        # Fix Pylance
        from thordata._utils import build_builder_headers
        headers = build_builder_headers(
            self.client.scraper_token or "",
            self.client.public_token or "",
            self.client.public_key or ""
        )

        print(f"   ⚡ Sending Raw Payload (spider_universal): {json.dumps(spider_universal)}")

        # Post to /video_builder
        response = self.client._api_request_with_retry(
            "POST", 
            self.client._video_builder_url, 
            data=payload, 
            headers=headers
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") != 200:
            raise Exception(f"Video Builder API Error: {data}")
            
        return data["data"]["task_id"]

    def _run_spider(self, config_key: str, input_value: str, dynamic_params: Optional[Dict[str, Any]] = None) -> Optional[str]:
        cfg = SPIDER_REGISTRY.get(config_key)
        if not cfg:
            print(f"❌ Registry Key Not Found: {config_key}")
            return None

        final_params = {cfg.input_key: input_value}
        if cfg.extra_params: final_params.update(cfg.extra_params)
        if dynamic_params: final_params.update(dynamic_params)

        print(f"🕵️ [Smart Route] Using: {cfg.desc} ({cfg.id})")

        try:
            task_id = ""
            
            if cfg.is_video:
                # Bypass SDK Wrapper for Video
                task_id = self._create_video_task_raw(cfg, final_params)
            else:
                # Standard Data Task
                task_id = self.client.create_scraper_task(
                    file_name=f"rag_{cfg.id}",
                    spider_id=cfg.id,
                    spider_name=cfg.name,
                    parameters=final_params
                )
            
            print(f"   ⏳ Task {task_id} created. Polling...")
            
            # Manual Polling
            start_time = time.time()
            download_url = ""
            
            while (time.time() - start_time) < 600:
                status = self.client.get_task_status(task_id)
                if status.lower() in ["ready", "success", "finished"]:
                    download_url = self.client.get_task_result(task_id)
                    break
                if status.lower() in ["failed", "error", "cancelled"]:
                    raise Exception(f"Task {task_id} ended with status: {status}")
                time.sleep(3)

            if not download_url:
                raise Exception("Timeout waiting for task")

            # --- Download & Clean ---
            print(f"   ⬇️ Downloading data...")
            resp = requests.get(download_url, timeout=60)
            
            try:
                data = resp.json()
            except Exception:
                return resp.text
            
            if isinstance(data, list):
                if not data: return None
                if len(data) == 1: return json.dumps(data[0], indent=2, ensure_ascii=False)
            
            return json.dumps(data, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"⚠️ Task Execution Failed: {e}")
            return None

    def route_and_scrape(self, url: str) -> Optional[str]:
        parsed = urlparse(url)
        path = parsed.path
        query = parse_qs(parsed.query)
        domain = parsed.netloc.lower()

        # === Amazon ===
        if "amazon" in domain:
            if "/s" in url and "k" in query:
                return self._run_spider("amazon_search", query["k"][0], {"domain": f"{parsed.scheme}://{parsed.netloc}/"})
            if "product-reviews" in url: return self._run_spider("amazon_review", url)
            if "seller=" in url or "/sp?" in url: return self._run_spider("amazon_seller", url)
            return self._run_spider("amazon_product", url, {"country": "us"})

        # === Google Maps ===
        elif "google.com/maps" in url:
            if "reviews" in url: return self._run_spider("gmaps_review", url)
            return self._run_spider("gmaps_detail", url)

        # === YouTube ===
        elif "youtube.com" in domain or "youtu.be" in domain:
            if "v=" in url or "youtu.be" in domain:
                return self._run_spider("youtube_video", url)
            elif "@" in path or "/channel/" in path:
                return self._run_spider("youtube_channel", url)

        # === TikTok ===
        elif "tiktok.com" in domain:
            if "/video/" in path: return self._run_spider("tiktok_post", url)
            if "@" in path: return self._run_spider("tiktok_profile", url)
            if "shop" in path: return self._run_spider("tiktok_shop", url)
            return self._run_spider("tiktok_comment", url)

        # === Google Play ===
        elif "play.google.com" in domain:
            return self._run_spider("play_store_app", url)

        # === Instagram ===
        elif "instagram.com" in domain:
            if "/reel/" in path: return self._run_spider("ins_reel", url)
            if "/p/" in path: return self._run_spider("ins_comment", url) 
            parts = [p for p in path.split("/") if p]
            if len(parts) == 1 and parts[0] not in ("explore", "direct"):
                return self._run_spider("ins_profile", parts[0])
            return self._run_spider("ins_post", url)

        # === Facebook ===
        elif "facebook.com" in domain:
            if "/search" in path and "q" in query: return self._run_spider("facebook_search", query["q"][0])
            return self._run_spider("facebook_post", url)

        # === Twitter/X ===
        elif "twitter.com" in domain or "x.com" in domain:
            if "/status/" in path: return self._run_spider("twitter_post", url)
            return self._run_spider("twitter_profile", url)

        # === LinkedIn ===
        elif "linkedin.com" in domain:
            if "/jobs/" in path: return self._run_spider("linkedin_job", url)
            return self._run_spider("linkedin_company", url)

        # === Reddit ===
        elif "reddit.com" in domain:
            if "/comments/" in path: return self._run_spider("reddit_comment", url)
            return self._run_spider("reddit_post", url)

        # === GitHub ===
        elif "github.com" in domain:
            return self._run_spider("github_repo", url)

        return None