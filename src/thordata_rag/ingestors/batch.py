"""Batch processing utilities for multiple URLs."""
from __future__ import annotations

import asyncio
import logging
from typing import List, Optional, Tuple

from ..core.config import settings
from .router import SmartRouter

logger = logging.getLogger(__name__)


class BatchProcessor:
    """Batch processor for handling multiple URLs concurrently."""

    def __init__(
        self,
        router: Optional[SmartRouter] = None,
        max_concurrency: int = 5,
    ):
        """Initialize the batch processor.

        Args:
            router: Optional SmartRouter instance
            max_concurrency: Maximum concurrent requests
        """
        self.router = router or SmartRouter()
        self.max_concurrency = max_concurrency

    async def process_urls(
        self,
        urls: List[str],
        prefer_structured: bool = True,
    ) -> List[Tuple[str, str, str]]:
        """Process multiple URLs concurrently.

        Args:
            urls: List of URLs to process
            prefer_structured: Whether to prefer structured data

        Returns:
            List of tuples (url, content, route_type)
        """
        semaphore = asyncio.Semaphore(self.max_concurrency)
        results = []

        async def process_one(url: str) -> Tuple[str, str, str]:
            async with semaphore:
                try:
                    content, route_type = await self.router.scrape(
                        url=url,
                        prefer_structured=prefer_structured,
                    )
                    return (url, content, route_type)
                except Exception as e:
                    logger.error(f"Failed to process {url}: {e}")
                    return (url, "", "error")

        tasks = [process_one(url) for url in urls]
        results = await asyncio.gather(*tasks)

        successful = sum(1 for _, content, _ in results if content)
        logger.info(f"Batch processing complete: {successful}/{len(urls)} successful")

        return results
