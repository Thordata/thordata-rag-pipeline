"""
RAG Data Pipeline CLI

This script demonstrates how to:
1. Use Thordata's Universal Scraping API to fetch a fully rendered web page.
2. Clean noisy HTML into Markdown-style text suitable for RAG / LLMs.
3. Save the result to a local file (e.g. knowledge_base_sample.md).

Usage (from the repository root):

    python -m scripts.rag_data_pipeline \
        --url https://openai.com/research/ \
        --output data/openai_research.md

You can also customize JS rendering, country, and resource blocking.
"""

from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from thordata import ThordataClient

# ---------------------------------------------------------------------------
# Configuration & logging
# ---------------------------------------------------------------------------

# Resolve project root (two levels above this file: scripts/ -> repo root)
ROOT_DIR = Path(__file__).resolve().parents[1]

# Ensure we always load the .env from the repo root, no matter where we run from
ENV_PATH = ROOT_DIR / ".env"
load_dotenv(ENV_PATH)

logger = logging.getLogger("thordata.rag")


# ---------------------------------------------------------------------------
# HTML -> Markdown cleaning
# ---------------------------------------------------------------------------


def clean_html_to_markdown(html_content: str) -> str:
    """
    Convert messy HTML into Markdown-style text suitable for RAG / LLMs.

    The logic here is intentionally simple and opinionated:
    - Remove scripts, styles, navigation, and other non-content elements.
    - Extract headings (h1–h3) and paragraphs.
    - Skip very short paragraphs that are likely boilerplate.

    Args:
        html_content: Raw HTML string.

    Returns:
        A Markdown-like string containing cleaned text.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # 1. Remove irrelevant tags (ads, navigation, scripts, etc.)
    for tag in soup(["script", "style", "nav", "footer", "iframe", "noscript"]):
        tag.decompose()

    # 2. Collect headings and paragraphs
    markdown_lines: list[str] = []

    # Headings (H1–H3)
    for heading in soup.find_all(["h1", "h2", "h3"]):
        level = int(heading.name[1])
        prefix = "#" * level
        markdown_lines.append(f"\n{prefix} {heading.get_text(strip=True)}\n")

    # Paragraphs
    for p in soup.find_all("p"):
        text = p.get_text(strip=True)
        # Filter out very short / noisy text
        if len(text) > 20:
            markdown_lines.append(text)

    return "\n".join(markdown_lines)


# ---------------------------------------------------------------------------
# CLI argument parsing
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="RAG Data Pipeline using Thordata Universal Scraping API",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--url",
        type=str,
        default="https://openai.com/research/",
        help="Target URL to scrape.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="knowledge_base_sample.md",
        help="Path of the output markdown file.",
    )
    parser.add_argument(
        "--country",
        type=str,
        default=None,
        help="Optional geo-targeting country code (e.g. 'us', 'de').",
    )
    parser.add_argument(
        "--no-js",
        dest="js_render",
        action="store_false",
        help="Disable JavaScript rendering to speed up scraping.",
    )
    parser.set_defaults(js_render=True)
    parser.add_argument(
        "--block-resources",
        action="store_true",
        help="Block images/css to speed up page load.",
    )

    return parser.parse_args()


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------


def build_client() -> ThordataClient:
    """Initialize ThordataClient from environment variables."""
    scraper_token = os.getenv("THORDATA_SCRAPER_TOKEN")
    public_token = os.getenv("THORDATA_PUBLIC_TOKEN")
    public_key = os.getenv("THORDATA_PUBLIC_KEY")

    if not scraper_token:
        raise RuntimeError(
            "THORDATA_SCRAPER_TOKEN is missing. "
            "Please create a .env file at the project root and set your tokens."
        )

    return ThordataClient(
        scraper_token=scraper_token,
        public_token=public_token,
        public_key=public_key,
    )


def run_pipeline(
    url: str,
    output_path: Path,
    js_render: bool = True,
    country: str | None = None,
    block_resources: bool = False,
) -> None:
    """
    Run the full RAG pipeline for a single URL.

    Args:
        url: Target URL.
        output_path: Path to the markdown output file.
        js_render: Whether to enable JS rendering.
        country: Optional country code for geo-targeting.
        block_resources: Whether to block heavy resources.
    """
    client = build_client()

    logger.info("Starting RAG pipeline for URL: %s", url)
    logger.info(
        "Options -> js_render=%s, country=%s, block_resources=%s",
        js_render,
        country,
        block_resources,
    )

    # 1. Fetch rendered HTML via Universal API
    logger.info("Requesting Universal Scraper...")
    html = client.universal_scrape(
        url=url,
        js_render=js_render,
        output_format="HTML",
        country=country,
        block_resources=block_resources,
    )
    logger.info("Scrape success. HTML length: %d characters", len(html))

    # 2. Clean & transform HTML into Markdown-like text
    logger.info("Cleaning and transforming HTML...")
    markdown_content = clean_html_to_markdown(html)

    # Ensure parent directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 3. Save result to file
    logger.info("Saving markdown to %s", output_path)
    with output_path.open("w", encoding="utf-8") as f:
        f.write(f"Source: {url}\n\n")
        f.write(markdown_content)

    logger.info("Pipeline completed successfully.")
    logger.info("Output file is ready for vector database embedding.")


def main() -> None:
    args = parse_args()
    try:
        output_path = (ROOT_DIR / args.output).resolve()
        run_pipeline(
            url=args.url,
            output_path=output_path,
            js_render=args.js_render,
            country=args.country,
            block_resources=args.block_resources,
        )
    except Exception as exc:
        logger.error("Pipeline failed: %s", exc, exc_info=True)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(message)s",
    )
    main()
