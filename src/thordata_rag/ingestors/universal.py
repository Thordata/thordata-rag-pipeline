"""Universal web scraper using Thordata's Web Unlocker."""
from __future__ import annotations

import logging
import re
from typing import Optional

from bs4 import BeautifulSoup
from markdownify import markdownify as md
from thordata import AsyncThordataClient

from ..core.config import settings

logger = logging.getLogger(__name__)


class UniversalIngestor:
    """Universal web scraper that handles any URL via Thordata's Web Unlocker."""

    def __init__(self, scraper_token: Optional[str] = None):
        """Initialize the universal ingestor.

        Args:
            scraper_token: Optional scraper token. If not provided, uses settings.
        """
        self.scraper_token = scraper_token or settings.THORDATA_SCRAPER_TOKEN

    def _clean_html(self, html: str) -> str:
        """Clean HTML by removing unnecessary elements while preserving structure.

        Args:
            html: Raw HTML content

        Returns:
            Cleaned HTML string
        """
        soup = BeautifulSoup(html, "lxml")

        # Remove script, style, and other non-content elements
        for tag in soup(
            ["script", "style", "noscript", "iframe", "meta", "link", "svg", "button", "input", "form"]
        ):
            tag.decompose()

        # Remove navigation and footer elements
        for tag in soup(["nav", "footer", "header", "aside"]):
            tag.decompose()

        # Prefer <article> tag if present (common for blog/news sites)
        article = soup.find("article")
        if article:
            return str(article)

        return str(soup.body) if soup.body else str(soup)

    async def scrape_to_markdown(
        self,
        url: str,
        country: Optional[str] = None,
        js_render: Optional[bool] = None,
        wait_ms: int = 2000,
    ) -> str:
        """Scrape a URL and convert to markdown.

        Args:
            url: Target URL to scrape
            country: Optional country code for geolocation
            js_render: Whether to enable JavaScript rendering
            wait_ms: Wait time in milliseconds before capture

        Returns:
            Markdown content string
        """
        logger.info(f"Scraping URL: {url} (Region: {country or 'Auto'})")

        try:
            js_render = js_render if js_render is not None else settings.ENABLE_JS_RENDER
            country = country or settings.DEFAULT_COUNTRY

            async with AsyncThordataClient(scraper_token=self.scraper_token) as client:
                # Use new namespace API
                html = await client.universal.scrape_async(
                    url=url,
                    js_render=js_render,
                    country=country,
                    wait_time=wait_ms,
                    output_format="html",
                    block_resources="image,media",
                )

            html_str = str(html) if not isinstance(html, str) else html

            # Clean HTML
            cleaned_html = self._clean_html(html_str)

            # Convert to markdown
            markdown = md(cleaned_html, heading_style="ATX")

            # Post-process: compress consecutive blank lines
            markdown = re.sub(r"\n\s*\n", "\n\n", markdown)

            logger.info(f"Extracted content: {len(markdown)} characters")
            return markdown

        except Exception as e:
            logger.error(f"Universal scraping failed for {url}: {e}")
            return f"Universal Scraping Failed: {str(e)}"
