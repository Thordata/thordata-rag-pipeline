import unittest
import sys
import os

# 将 src 加入路径以便导入
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.thordata_rag.ingestors.specialized import SpecializedIngestor
from src.thordata_rag.ingestors.registry import SPIDER_REGISTRY

class TestRouterMatrix(unittest.TestCase):
    def setUp(self):
        # 伪造 Token，只测试路由逻辑
        self.ingestor = SpecializedIngestor("dummy", "dummy", "dummy")
        # Mock _run_spider 拦截调用，返回它命中的配置 Key
        self.ingestor._run_spider = self.mock_run

    def mock_run(self, config_key, input_value, dynamic_params=None):
        cfg = SPIDER_REGISTRY.get(config_key)
        return {
            "key": config_key,
            "spider_id": cfg.id if cfg else "UNKNOWN",
            "input_val": input_value,
            "is_video": cfg.is_video if cfg else False
        }

    # === Amazon 测试 ===
    def test_amazon_routes(self):
        # 搜索页 (含有 k=)
        r = self.ingestor.route_and_scrape("https://www.amazon.com/s?k=laptop")
        self.assertEqual(r['key'], "amazon_search")
        self.assertEqual(r['input_val'], "laptop")

        # 详情页 (URL)
        r = self.ingestor.route_and_scrape("https://www.amazon.com/dp/B08N5WRWNW")
        self.assertEqual(r['key'], "amazon_product")
        
        # 评论页
        r = self.ingestor.route_and_scrape("https://www.amazon.com/product-reviews/B08N5WRWNW")
        self.assertEqual(r['key'], "amazon_review")

        # 卖家页
        r = self.ingestor.route_and_scrape("https://www.amazon.com/sp?seller=A123")
        self.assertEqual(r['key'], "amazon_seller")

    # === Google 测试 ===
    def test_google_routes(self):
        # Maps
        r = self.ingestor.route_and_scrape("https://www.google.com/maps/place/Eiffel+Tower")
        self.assertEqual(r['key'], "gmaps_detail")
        
        # Play Store
        r = self.ingestor.route_and_scrape("https://play.google.com/store/apps/details?id=com.whatsapp")
        self.assertEqual(r['key'], "play_store_app")

    # === Social Media 测试 ===
    def test_social_routes(self):
        # TikTok Video
        r = self.ingestor.route_and_scrape("https://www.tiktok.com/@user/video/123456")
        self.assertEqual(r['key'], "tiktok_post")
        self.assertTrue(r['is_video'])

        # TikTok Profile
        r = self.ingestor.route_and_scrape("https://www.tiktok.com/@tiktok")
        self.assertEqual(r['key'], "tiktok_profile")

        # YouTube Video
        r = self.ingestor.route_and_scrape("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        self.assertEqual(r['key'], "youtube_video")
        self.assertTrue(r['is_video'])

        # LinkedIn Company
        r = self.ingestor.route_and_scrape("https://www.linkedin.com/company/google")
        self.assertEqual(r['key'], "linkedin_company")

if __name__ == '__main__':
    unittest.main()