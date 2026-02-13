"""Automatic spider discovery from Thordata SDK."""
from __future__ import annotations

import logging
from typing import Dict, Optional

from thordata import AsyncThordataClient
# Import internal registry functions
# Note: These are internal but necessary for spider discovery
try:
    from thordata._tools_registry import (
        _iter_tool_classes,
        _tool_group_from_class,
        _tool_key_from_class,
    )
except ImportError:
    # Fallback if internal functions are not available
    def _iter_tool_classes():
        return []
    
    def _tool_group_from_class(cls):
        return "default"
    
    def _tool_key_from_class(cls):
        return getattr(cls, "SPIDER_ID", cls.__name__.lower())
from thordata.tools import ToolRequest

from ..core.config import settings
from .registry import SPIDER_REGISTRY, SpiderConfig

logger = logging.getLogger(__name__)


class SpiderDiscovery:
    """Automatic discovery of all available spiders from SDK."""

    def __init__(self):
        """Initialize spider discovery."""
        self._discovered_spiders: Optional[Dict[str, SpiderConfig]] = None

    def discover_all_spiders(self) -> Dict[str, SpiderConfig]:
        """Discover all available spiders from SDK.

        Returns:
            Dictionary mapping registry keys to SpiderConfig objects
        """
        if self._discovered_spiders is not None:
            return self._discovered_spiders

        discovered = {}
        tool_classes = list(_iter_tool_classes())

        logger.info(f"Discovering spiders from SDK... Found {len(tool_classes)} tool classes")

        for tool_class in tool_classes:
            try:
                spider_id = getattr(tool_class, "SPIDER_ID", "")
                spider_name = getattr(tool_class, "SPIDER_NAME", "")
                tool_key = _tool_key_from_class(tool_class)
                group = _tool_group_from_class(tool_class)

                if not spider_id:
                    continue

                # Check if it's a video tool
                from thordata.tools import VideoToolRequest

                is_video = issubclass(tool_class, VideoToolRequest)

                # Create registry key from spider_id
                registry_key = spider_id.replace("-", "_").replace("_by-", "_")

                # Extract input key from dataclass fields
                input_key = "url"  # default
                if hasattr(tool_class, "__dataclass_fields__"):
                    fields = tool_class.__dataclass_fields__
                    # Find the first non-internal field
                    for field_name, field_info in fields.items():
                        if not field_name.startswith("_") and field_name not in [
                            "common_settings",
                            "SPIDER_ID",
                            "SPIDER_NAME",
                        ]:
                            input_key = field_name
                            break

                # Create config
                config = SpiderConfig(
                    id=spider_id,
                    name=spider_name,
                    desc=f"{group}.{spider_id}",
                    input_key=input_key,
                    is_video=is_video,
                )

                discovered[registry_key] = config
                logger.debug(f"Discovered: {registry_key} -> {spider_id}")

            except Exception as e:
                logger.warning(f"Failed to process tool class {tool_class}: {e}")
                continue

        logger.info(f"Successfully discovered {len(discovered)} spiders")
        self._discovered_spiders = discovered
        return discovered

    def get_merged_registry(self) -> Dict[str, SpiderConfig]:
        """Get merged registry (manual + discovered).

        Returns:
            Merged dictionary of all available spiders
        """
        manual = SPIDER_REGISTRY.copy()
        discovered = self.discover_all_spiders()

        # Merge: discovered spiders override manual ones if key conflicts
        merged = {**manual, **discovered}

        logger.info(f"Registry merged: {len(manual)} manual + {len(discovered)} discovered = {len(merged)} total")
        return merged

    def find_spider_by_url(self, url: str) -> Optional[str]:
        """Find the best spider for a given URL.

        Args:
            url: Target URL

        Returns:
            Registry key of the best matching spider, or None
        """
        from urllib.parse import urlparse

        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()

        # Try to match by domain and path patterns
        registry = self.get_merged_registry()

        # Exact domain match
        for key, config in registry.items():
            if config.name.lower() in domain:
                # Additional path matching for better accuracy
                if "youtube" in key and ("watch" in path or "youtu.be" in domain):
                    return key
                if "amazon" in key and ("/dp/" in path or "/product/" in path):
                    return key
                return key

        return None
