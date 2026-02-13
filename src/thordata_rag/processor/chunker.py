"""Document chunking utilities for RAG pipeline."""
from __future__ import annotations

import logging
from typing import List

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    # Fallback for older langchain versions
    from langchain.text_splitter import RecursiveCharacterTextSplitter

from ..core.config import settings

logger = logging.getLogger(__name__)

# Token limit for embedding API (SiliconFlow: 512 tokens per input)
# Approximate: 1 token ≈ 4 characters for English, 2-3 for Chinese
# Use 400 chars per chunk to be safe (≈100-200 tokens)
EMBEDDING_TOKEN_LIMIT = 400  # Characters per chunk for embedding API compatibility


class DocumentChunker:
    """Chunks documents for vector storage."""

    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ):
        """Initialize the document chunker.

        Args:
            chunk_size: Size of each chunk in characters
            chunk_overlap: Overlap between chunks in characters
        """
        # Use smaller chunk size for embedding API compatibility
        # SiliconFlow has 512 token limit per input
        default_chunk_size = min(settings.CHUNK_SIZE, EMBEDDING_TOKEN_LIMIT)
        self.chunk_size = chunk_size or default_chunk_size
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def chunk_text(self, text: str, metadata: dict | None = None) -> List[dict]:
        """Split text into chunks with metadata.

        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to each chunk

        Returns:
            List of chunk dictionaries with 'text' and 'metadata' keys
        """
        if not text or len(text.strip()) == 0:
            logger.warning("Empty text provided for chunking")
            return []

        # Truncate if too long
        max_length = settings.MAX_CONTENT_LENGTH
        if len(text) > max_length:
            logger.warning(f"Text truncated from {len(text)} to {max_length} characters")
            text = text[:max_length]

        chunks = self.splitter.split_text(text)

        result = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = {
                "chunk_index": i,
                "total_chunks": len(chunks),
                **(metadata or {}),
            }
            result.append({"text": chunk, "metadata": chunk_metadata})

        logger.info(f"Created {len(result)} chunks from text ({len(text)} chars)")
        return result
