import os
import sys
import json
import time
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath("src"))
from thordata_rag.ingestors.specialized import SpecializedIngestor

load_dotenv()

def test():
    print("🚀 Starting RAG Pipeline Verification...")
    
    token = os.getenv("THORDATA_SCRAPER_TOKEN")
    if not token:
        print("❌ Error: THORDATA_SCRAPER_TOKEN missing")
        return

    ingestor = SpecializedIngestor(
        scraper_token=token,
        public_token=os.getenv("THORDATA_PUBLIC_TOKEN"),
        public_key=os.getenv("THORDATA_PUBLIC_KEY")
    )

    # Use Big Buck Bunny (Safe, public)
    url = "https://www.youtube.com/watch?v=aqz-KE-bpKQ"
    
    print(f"\n📺 Testing YouTube Video: {url}")
    print("   (Using RAW Payload Bypass for maximum compatibility)")

    try:
        res_json_str = ingestor.route_and_scrape(url)
        
        if not res_json_str:
            print("❌ Result is None")
            return

        try:
            data = json.loads(res_json_str)
            print("   ✅ Valid JSON received")
            
            if isinstance(data, dict):
                title = data.get('title', 'Unknown')
                print(f"   🎥 Video Title: {title}")
            elif isinstance(data, list) and len(data) > 0:
                print(f"   🎥 Item 0: {str(data[0])[:50]}...")
            
            print("\n✨ RAG Pipeline Test PASSED")
            
        except json.JSONDecodeError:
            print(f"   ⚠️ Result is not JSON: {res_json_str[:100]}...")

    except Exception as e:
        print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    test()