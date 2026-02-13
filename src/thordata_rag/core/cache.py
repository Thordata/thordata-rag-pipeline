"""Simple in-memory cache for scraped content."""
from __future__ import annotations

import hashlib
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)


class SimpleCache:
    """Simple in-memory cache with TTL support."""

    def __init__(self, ttl: int = 3600):
        """Initialize the cache.

        Args:
            ttl: Time to live in seconds
        """
        self.cache: dict[str, tuple[float, str]] = {}
        self.ttl = ttl

    def _make_key(self, url: str) -> str:
        """Generate cache key from URL.

        Args:
            url: URL to generate key for

        Returns:
            Cache key string
        """
        return hashlib.md5(url.encode()).hexdigest()

    def get(self, url: str) -> Optional[str]:
        """Get cached content for URL.

        Args:
            url: URL to get cached content for

        Returns:
            Cached content or None if not found/expired
        """
        key = self._make_key(url)
        if key not in self.cache:
            return None

        timestamp, content = self.cache[key]
        if time.time() - timestamp > self.ttl:
            # Expired
            del self.cache[key]
            return None

        logger.debug(f"Cache hit for: {url}")
        return content

    def set(self, url: str, content: str):
        """Cache content for URL.

        Args:
            url: URL to cache
            content: Content to cache
        """
        key = self._make_key(url)
        self.cache[key] = (time.time(), content)
        logger.debug(f"Cached content for: {url}")

    def clear(self):
        """Clear all cached content."""
        self.cache.clear()
        logger.info("Cache cleared")

    def size(self) -> int:
        """Get number of cached items.

        Returns:
            Number of cached items
        """
        return len(self.cache)
