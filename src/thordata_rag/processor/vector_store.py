"""Vector store integration using ChromaDB."""
from __future__ import annotations

import logging
import os
from typing import List, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_openai import OpenAIEmbeddings

from ..core.llm_config import get_embedding_model

# Use langchain-chroma if available, fallback to langchain_community
try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma

from ..core.config import settings

logger = logging.getLogger(__name__)


class VectorStore:
    """Vector store manager for RAG pipeline."""

    def __init__(
        self,
        collection_name: str | None = None,
        persist_directory: str | None = None,
    ):
        """Initialize the vector store.

        Args:
            collection_name: Name of the ChromaDB collection
            persist_directory: Directory to persist the database
        """
        self.collection_name = collection_name or settings.COLLECTION_NAME
        self.persist_directory = persist_directory or settings.DB_PATH

        # Ensure directory exists
        os.makedirs(self.persist_directory, exist_ok=True)

        # Initialize embeddings with auto-detection
        embedding_model = get_embedding_model()
        # For SiliconFlow, try without model first (uses default)
        # If that fails, user should specify OPENAI_EMBEDDING_MODEL in .env
        # Always use model if specified, regardless of provider
        if embedding_model:
            self.embeddings = OpenAIEmbeddings(
                model=embedding_model,
                openai_api_key=settings.OPENAI_API_KEY,
                openai_api_base=settings.OPENAI_API_BASE,
            )
        else:
            # For SiliconFlow or when model is None, try without model parameter
            # This will use the default embedding model from the API
            try:
                self.embeddings = OpenAIEmbeddings(
                    openai_api_key=settings.OPENAI_API_KEY,
                    openai_api_base=settings.OPENAI_API_BASE,
                )
            except Exception as e:
                logger.warning(f"Failed to initialize embeddings without model: {e}")
                # Last resort: use a simple text-based approach or raise
                raise ValueError(
                    f"Could not initialize embeddings. "
                    f"Please set OPENAI_EMBEDDING_MODEL in .env to a valid model for {settings.OPENAI_API_BASE}"
                )

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=ChromaSettings(anonymized_telemetry=False),
        )

        # Initialize or get collection
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Loaded existing collection: {self.collection_name}")
        except Exception:
            self.collection = self.client.create_collection(name=self.collection_name)
            logger.info(f"Created new collection: {self.collection_name}")

        # Initialize LangChain Chroma wrapper
        self.vectorstore = Chroma(
            client=self.client,
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory,
        )

    def add_documents(self, texts: List[str], metadatas: List[dict] | None = None, ids: List[str] | None = None):
        """Add documents to the vector store.

        Args:
            texts: List of text documents to add
            metadatas: Optional list of metadata dictionaries
            ids: Optional list of document IDs
        """
        if not texts:
            logger.warning("No texts provided to add_documents")
            return

        # Batch size limit for embedding API (SiliconFlow limit is 32)
        batch_size = 30  # Use 30 to be safe
        
        try:
            # Process in batches if needed
            if len(texts) > batch_size:
                logger.info(f"Processing {len(texts)} documents in batches of {batch_size}")
                total_added = 0
                for i in range(0, len(texts), batch_size):
                    batch_texts = texts[i:i + batch_size]
                    batch_metadatas = metadatas[i:i + batch_size] if metadatas else None
                    batch_ids = ids[i:i + batch_size] if ids else None
                    
                    self.vectorstore.add_texts(
                        texts=batch_texts,
                        metadatas=batch_metadatas,
                        ids=batch_ids,
                    )
                    total_added += len(batch_texts)
                    logger.debug(f"Added batch {i//batch_size + 1}: {len(batch_texts)} documents")
                logger.info(f"Added {total_added} documents to vector store in {(len(texts) + batch_size - 1) // batch_size} batches")
            else:
                # Single batch
                self.vectorstore.add_texts(
                    texts=texts,
                    metadatas=metadatas,
                    ids=ids,
                )
                logger.info(f"Added {len(texts)} documents to vector store")
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to add documents: {error_msg}")
            # Provide helpful error messages
            if "Model does not exist" in error_msg or "20012" in error_msg:
                raise ValueError(
                    f"Embedding model error. Please set OPENAI_EMBEDDING_MODEL in .env "
                    f"to a valid model for {settings.OPENAI_API_BASE}."
                ) from e
            if "batch size" in error_msg.lower() or "20042" in error_msg or "413" in error_msg:
                raise ValueError(
                    f"Batch size too large. The embedding API has a limit. "
                    f"Try reducing CHUNK_SIZE in .env to create fewer chunks."
                ) from e
            raise

    def search(
        self,
        query: str,
        k: int = 5,
        filter: dict | None = None,
    ) -> List[dict]:
        """Search for similar documents.

        Args:
            query: Search query
            k: Number of results to return
            filter: Optional metadata filter

        Returns:
            List of search results with 'text' and 'metadata' keys
        """
        try:
            results = self.vectorstore.similarity_search_with_score(
                query=query,
                k=k,
                filter=filter,
            )

            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "text": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score),
                })

            logger.info(f"Found {len(formatted_results)} results for query")
            return formatted_results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def delete_collection(self):
        """Delete the collection (use with caution)."""
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")

    def get_collection_count(self) -> int:
        """Get the number of documents in the collection.

        Returns:
            Number of documents
        """
        try:
            count = self.collection.count()
            return count
        except Exception as e:
            logger.error(f"Failed to get collection count: {e}")
            return 0
