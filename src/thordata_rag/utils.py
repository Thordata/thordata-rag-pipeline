"""Utility functions for Thordata RAG Pipeline."""
import sys


def setup_console_encoding():
    """Setup console encoding for Windows compatibility."""
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass  # Ignore if already configured or not available
