import requests
import json
import re
from typing import Optional
from urllib.parse import urlparse, parse_qs
from thordata import ThordataClient, CommonSettings
from .registry import SPIDER_REGISTRY, SpiderConfig

class SpecializedIngestor:
    def __init__(self, scraper_token: str, public_token: Optional[str] = None, public_key: Optional[str] = None):
        self.client = ThordataClient(
            scraper_token=scraper_token,
            public_token=public_token,
            public_key=public_key
        )

    def _run_spider(self, config_key: str, input_value: str, dynamic_params: dict = None) -> Optional[str]:
        cfg = SPIDER_REGISTRY.get(config_key)
        if not cfg:
            print(f"❌ Registry Key Not Found: {config_key}")
            return None

        # 1. Build Parameters
        final_params = {cfg.input_key: input_value}
        if cfg.extra_params: final_params.update(cfg.extra_params)
        if dynamic_params: final_params.update(dynamic_params)

        print(f"🕵️ [Smart Route] Using: {cfg.desc} ({cfg.id}) | Mode: {'Video' if cfg.is_video else 'Data'}")

        try:
            download_url = ""
            
            if cfg.is_video:
                
                settings = CommonSettings(
                    resolution="720p",   # try 720p
                    is_subtitles="true",
                    audio_format="mp3"
                )
                
                task_id = self.client.create_video_task(
                    file_name=f"rag_vid_{cfg.id}",
                    spider_id=cfg.id,
                    spider_name=cfg.name,
                    parameters=final_params,
                    common_settings=settings
                )
                
                status = self.client.wait_for_task(task_id, max_wait=600)
                if status.lower() not in ("ready", "success", "finished"):
                    raise Exception(f"Video Task failed: {status}")
                download_url = self.client.get_task_result(task_id)
            
            else:
                # Data Task (Google Maps 等走这里)
                download_url = self.client.run_task(
                    file_name=f"rag_{cfg.id}",
                    spider_id=cfg.id,
                    spider_name=cfg.name,
                    parameters=final_params,
                    include_errors=True
                )
            
            # --- Download & Clean ---
            print(f"⬇️ Downloading data...")
            resp = requests.get(download_url, timeout=60)
            data = resp.json()
            
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
            if "/s" in url and "k=" in url:
                if "k" in query: return self._run_spider("amazon_search", query["k"][0], {"domain": f"{parsed.scheme}://{parsed.netloc}/"})
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
                return self._run_spider("youtube_post", url)

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