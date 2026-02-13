"""Smart router that automatically selects the best scraping strategy."""
from __future__ import annotations

import logging
from typing import Optional

from .specialized import SpecializedIngestor
from .universal import UniversalIngestor

logger = logging.getLogger(__name__)


class SmartRouter:
    """Intelligent router that selects the best scraping strategy for a URL."""

    def __init__(
        self,
        scraper_token: Optional[str] = None,
        public_token: Optional[str] = None,
        public_key: Optional[str] = None,
    ):
        """Initialize the smart router.

        Args:
            scraper_token: Optional scraper token
            public_token: Optional public token
            public_key: Optional public key
        """
        self.specialized = SpecializedIngestor(
            scraper_token=scraper_token,
            public_token=public_token,
            public_key=public_key,
        )
        self.universal = UniversalIngestor(scraper_token=scraper_token)

    async def scrape(
        self,
        url: str,
        prefer_structured: bool = True,
        fallback_to_universal: bool = True,
    ) -> tuple[str, str]:
        """Scrape a URL using the best available strategy.

        Args:
            url: Target URL to scrape
            prefer_structured: Whether to prefer structured data (specialized spiders)
            fallback_to_universal: Whether to fallback to universal scraper if specialized fails

        Returns:
            Tuple of (content, route_type) where route_type is 'specialized' or 'universal'
        """
        if prefer_structured:
            logger.info(f"Attempting specialized route for: {url}")
            content = await self.specialized.route_and_scrape(url)

            if content and len(content) > 200:
                logger.info("Successfully used specialized spider")
                return content, "specialized"

            if fallback_to_universal:
                logger.info("Specialized route failed or returned insufficient data, falling back to universal")
            else:
                logger.warning("Specialized route failed and fallback is disabled")
                return content or "", "specialized"

        # Use universal scraper
        logger.info(f"Using universal scraper for: {url}")
        content = await self.universal.scrape_to_markdown(url)
        return content, "universal"
