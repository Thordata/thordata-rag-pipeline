import os
import argparse
import sys
from dotenv import load_dotenv
from src.thordata_rag.ingestors.universal import UniversalIngestor
from src.thordata_rag.ingestors.specialized import SpecializedIngestor
from src.thordata_rag.core.config import settings
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# Force UTF-8 for Windows Consoles
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Thordata RAG Pipeline (Enterprise Edition)")
    parser.add_argument("--url", required=True, help="Target URL (Amazon, YouTube, News, etc.)")
    parser.add_argument("--question", required=True, help="Question to ask about the content")
    
    args = parser.parse_args()

    # 1. Ingestion Phase
    print(f"🚀 Initializing Pipeline for: {args.url}")
    
    specialized = SpecializedIngestor(
        settings.THORDATA_SCRAPER_TOKEN,
        settings.THORDATA_PUBLIC_TOKEN,
        settings.THORDATA_PUBLIC_KEY
    )
    
    # Try Smart Routing (L2 Specialized Spiders)
    content = specialized.route_and_scrape(args.url)
    
    if content:
        print("🔥 Route: Specialized Spider (Structured Data)")
    else:
        # Fallback to Universal (Headless Browser)
        print("💡 Route: Universal Web Scraper (Markdown)")
        ingestor = UniversalIngestor(settings.THORDATA_SCRAPER_TOKEN)
        # Auto-detect region for universal scraper
        region = "us" if "amazon" in args.url or "google" in args.url else None
        content = ingestor.scrape_to_markdown(args.url, country=region)

    # 2. Validation
    data_len = len(content)
    print(f"\n📦 Data Retrieved: {data_len} chars")
    
    if data_len < 200:
        print(f"⚠️ [WARNING] Data payload suspiciously small. Raw output:\n{content}\n")

    # 3. AI Analysis
    api_key = os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")

    if not api_key:
        print("❌ Error: OPENAI_API_KEY missing in .env")
        return

    print(f"🤖 Loading AI Model (Base: {api_base})...")
    llm = ChatOpenAI(
        model="Qwen/Qwen2.5-7B-Instruct", # Or your preferred model
        openai_api_key=api_key,
        openai_api_base=api_base,
        temperature=0.3
    )

    prompt = f"""
    You are an expert data analyst powered by Thordata.
    Analyze the provided raw data (JSON or Markdown) and answer the user's question accurately.

    --- DATA START ---
    {content[:50000]} 
    --- DATA END ---

    User Question: {args.question}
    """

    try:
        print("🧠 Analyzing...")
        response = llm.invoke([HumanMessage(content=prompt)])
        
        print("\n" + "="*30 + " Thordata Insight Report " + "="*30)
        print(response.content)
        print("="*85)
    except Exception as e:
        print(f"❌ AI Analysis Failed: {e}")

if __name__ == "__main__":
    main()