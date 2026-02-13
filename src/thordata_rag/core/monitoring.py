"""Performance monitoring and metrics collection."""
from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Simple performance monitoring for scraping operations."""

    def __init__(self):
        """Initialize the performance monitor."""
        self.metrics: Dict[str, list[float]] = {}
        self.counts: Dict[str, int] = {}

    @contextmanager
    def measure(self, operation: str):
        """Context manager to measure operation time.

        Args:
            operation: Operation name
        """
        start = time.time()
        try:
            yield
        finally:
            elapsed = time.time() - start
            if operation not in self.metrics:
                self.metrics[operation] = []
                self.counts[operation] = 0
            self.metrics[operation].append(elapsed)
            self.counts[operation] += 1
            logger.debug(f"{operation} took {elapsed:.2f}s")

    def get_stats(self, operation: str) -> Optional[Dict[str, float]]:
        """Get statistics for an operation.

        Args:
            operation: Operation name

        Returns:
            Dictionary with stats or None if no data
        """
        if operation not in self.metrics:
            return None

        times = self.metrics[operation]
        return {
            "count": len(times),
            "total": sum(times),
            "avg": sum(times) / len(times),
            "min": min(times),
            "max": max(times),
        }

    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        """Get statistics for all operations.

        Returns:
            Dictionary mapping operation names to their stats
        """
        return {op: self.get_stats(op) for op in self.metrics.keys() if self.get_stats(op) is not None}

    def reset(self):
        """Reset all metrics."""
        self.metrics.clear()
        self.counts.clear()


# Global instance
_monitor = PerformanceMonitor()


def get_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance.

    Returns:
        PerformanceMonitor instance
    """
    return _monitor
