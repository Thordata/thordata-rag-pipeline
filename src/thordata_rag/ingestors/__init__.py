"""Ingestors for scraping content from various sources."""
from .batch import BatchProcessor
from .router import SmartRouter
from .specialized import SpecializedIngestor
from .spider_discovery import SpiderDiscovery
from .universal import UniversalIngestor

__all__ = [
    "SmartRouter",
    "SpecializedIngestor",
    "UniversalIngestor",
    "SpiderDiscovery",
    "BatchProcessor",
]
