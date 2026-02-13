"""Main entry point for Thordata RAG Pipeline."""
import asyncio
import argparse
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from src.thordata_rag.core.config import settings
from src.thordata_rag.core.llm_config import get_model_name
from src.thordata_rag.core.cache import SimpleCache
from src.thordata_rag.ingestors.router import SmartRouter
from src.thordata_rag.processor.chunker import DocumentChunker
from src.thordata_rag.processor.vector_store import VectorStore

# Force UTF-8 for Windows consoles
from src.thordata_rag.utils import setup_console_encoding

setup_console_encoding()

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def ingest_and_store(
    url: str,
    router: SmartRouter,
    vector_store: VectorStore,
    chunker: DocumentChunker,
    cache: SimpleCache | None = None,
    use_cache: bool = True,
) -> tuple[str, str]:
    """Ingest content from URL and store in vector database.

    Args:
        url: URL to scrape
        router: Smart router instance
        vector_store: Vector store instance
        chunker: Document chunker instance
        cache: Optional cache instance
        use_cache: Whether to use cache

    Returns:
        Tuple of (content, route_type)
    """
    # Check cache first
    if use_cache and cache:
        cached_content = cache.get(url)
        if cached_content:
            logger.info("Using cached content")
            return cached_content, "cached"

    # Scrape content
    content, route_type = await router.scrape(url)

    if not content:
        logger.warning(f"No content retrieved")
        return "", route_type
    
    # Store even if content is short (minimum 50 chars)
    if len(content) < 50:
        logger.warning(f"Content very short: {len(content)} chars, skipping storage")
        return content, route_type

    # Chunk and store
    chunks = chunker.chunk_text(content, metadata={"url": url, "route_type": route_type})

    if chunks:
        texts = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        vector_store.add_documents(texts=texts, metadatas=metadatas)

        # Cache the content
        if use_cache and cache:
            cache.set(url, content)

    return content, route_type


async def query_rag(
    question: str,
    vector_store: VectorStore,
    llm: ChatOpenAI,
    k: int = 5,
) -> str:
    """Query the RAG system with a question.

    Args:
        question: User question
        vector_store: Vector store instance
        llm: Language model instance
        k: Number of relevant chunks to retrieve

    Returns:
        Answer string
    """
    # Search for relevant chunks
    results = vector_store.search(query=question, k=k)

    if not results:
        logger.warning("No relevant documents found in vector store")
        context = "No relevant context found."
    else:
        # Build context from retrieved chunks
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"[Document {i}]\n{result['text']}\n")
        context = "\n".join(context_parts)

    # Build prompt
    prompt = f"""You are an expert data analyst powered by Thordata RAG Pipeline.
Analyze the provided context and answer the user's question accurately and concisely.

--- CONTEXT START ---
{context}
--- CONTEXT END ---

User Question: {question}

Please provide a clear, accurate answer based on the context above. If the context doesn't contain enough information, say so."""

    try:
        logger.info("Querying LLM...")
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content
    except Exception as e:
        logger.error(f"LLM query failed: {e}")
        return f"Error: {str(e)}"


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Thordata RAG Pipeline - Intelligent web scraping and question answering",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape and answer a question
  python main.py --url "https://example.com" --question "What is this page about?"

  # Ingest only (no question)
  python main.py --url "https://example.com" --ingest-only

  # Query existing knowledge base
  python main.py --question "What did we learn about X?" --query-only

  # Batch process multiple URLs
  python main.py --urls "url1,url2,url3" --ingest-only
        """,
    )

    parser.add_argument("--url", help="Target URL to scrape")
    parser.add_argument("--urls", help="Comma-separated list of URLs to process")
    parser.add_argument("--question", help="Question to ask about the content")
    parser.add_argument(
        "--ingest-only",
        action="store_true",
        help="Only ingest content, don't query",
    )
    parser.add_argument(
        "--query-only",
        action="store_true",
        help="Only query existing knowledge base, don't scrape",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable caching",
    )
    parser.add_argument(
        "--k",
        type=int,
        default=5,
        help="Number of relevant chunks to retrieve (default: 5)",
    )
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear the cache before running",
    )

    args = parser.parse_args()

    # Validate arguments
    if args.query_only and not args.question:
        parser.error("--query-only requires --question")
    if not args.query_only and not args.url and not args.urls:
        parser.error("Either --url or --urls is required (unless using --query-only)")

    # Initialize components
    logger.info("Initializing RAG Pipeline components...")

    router = SmartRouter()
    chunker = DocumentChunker()
    vector_store = VectorStore()
    cache = SimpleCache(ttl=settings.CACHE_TTL) if settings.ENABLE_CACHE and not args.no_cache else None

    if args.clear_cache and cache:
        cache.clear()

    # Initialize LLM with auto-detection
    model_name = get_model_name()
    logger.info(f"Using LLM model: {model_name} (API: {settings.OPENAI_API_BASE})")
    llm = ChatOpenAI(
        model=model_name,
        openai_api_key=settings.OPENAI_API_KEY,
        openai_api_base=settings.OPENAI_API_BASE,
        temperature=settings.OPENAI_TEMPERATURE,
        max_tokens=settings.OPENAI_MAX_TOKENS,
    )

    try:
        # Handle query-only mode
        if args.query_only:
            logger.info("Query-only mode: searching existing knowledge base")
            answer = await query_rag(args.question, vector_store, llm, k=args.k)
            print("\n" + "=" * 80)
            print("[ANSWER]")
            print("=" * 80)
            print(answer)
            print("=" * 80)
            return

        # Process URLs
        urls = []
        if args.url:
            urls.append(args.url)
        if args.urls:
            urls.extend([u.strip() for u in args.urls.split(",") if u.strip()])

        for url in urls:
            logger.info(f"Processing URL: {url}")

            # Ingest content
            content, route_type = await ingest_and_store(
                url=url,
                router=router,
                vector_store=vector_store,
                chunker=chunker,
                cache=cache,
                use_cache=not args.no_cache,
            )

            print(f"\n{'=' * 80}")
            print(f"Content Retrieved: {len(content)} chars")
            print(f"Route: {route_type.upper()}")
            print(f"{'=' * 80}")

            if len(content) < 200:
                print(f"[WARN] Content payload suspiciously small")
                print(f"Raw output preview:\n{content[:500]}\n")

        # Query if question provided
        if args.question and not args.ingest_only:
            logger.info("Querying RAG system...")
            answer = await query_rag(args.question, vector_store, llm, k=args.k)

            print("\n" + "=" * 80)
            print("[ANSWER]")
            print("=" * 80)
            print(answer)
            print("=" * 80)

        # Show statistics
        doc_count = vector_store.get_collection_count()
        cache_size = cache.size() if cache else 0
        print(f"\n[STATS]")
        print(f"  Documents in vector store: {doc_count}")
        print(f"  Cached items: {cache_size}")

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
