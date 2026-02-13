"""Quick start script for Thordata RAG Pipeline - Simplified user experience."""
import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from thordata_rag.utils import setup_console_encoding
from thordata_rag.ingestors.router import SmartRouter
from thordata_rag.processor.chunker import DocumentChunker
from thordata_rag.processor.vector_store import VectorStore
from thordata_rag.core.llm_config import get_model_name
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

setup_console_encoding()
load_dotenv()


async def quick_scrape(url: str, question: str = None):
    """Quick scrape and optionally answer a question.
    
    Args:
        url: URL to scrape
        question: Optional question to ask
    """
    print(f"[*] Scraping: {url}")
    
    router = SmartRouter()
    chunker = DocumentChunker()
    vector_store = VectorStore()
    
    # Scrape
    content, route_type = await router.scrape(url)
    
    if not content or len(content) < 50:
        print(f"[ERROR] Failed to scrape or insufficient content ({len(content) if content else 0} chars)")
        return
    
    print(f"[OK] Scraped {len(content)} chars via {route_type}")
    
    # Store
    chunks = chunker.chunk_text(content, metadata={"url": url})
    if chunks:
        texts = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        vector_store.add_documents(texts=texts, metadatas=metadatas)
        print(f"[OK] Stored {len(chunks)} chunks")
    
    # Answer question if provided
    if question:
        print(f"\n[*] Answering: {question}")
        from thordata_rag.core.config import settings
        
        llm = ChatOpenAI(
            model=get_model_name(),
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_API_BASE,
            temperature=0.3,
        )
        
        results = vector_store.search(question, k=3)
        context = "\n".join([r["text"] for r in results])
        
        prompt = f"""Based on the following context, answer the question concisely.

Context:
{context}

Question: {question}

Answer:"""
        
        response = llm.invoke([HumanMessage(content=prompt)])
        print(f"\n[ANSWER]\n{response.content}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python quick_start.py <url> [question]")
        print("Example: python quick_start.py https://example.com 'What is this about?'")
        sys.exit(1)
    
    url = sys.argv[1]
    question = sys.argv[2] if len(sys.argv) > 2 else None
    
    asyncio.run(quick_scrape(url, question))
