"""LLM configuration helpers with auto-detection for different providers."""
from typing import Optional

from .config import settings


def get_model_name() -> str:
    """Auto-detect model name based on API base URL.

    Returns:
        Model name string
    """
    if settings.OPENAI_MODEL != "auto":
        return settings.OPENAI_MODEL

    api_base = settings.OPENAI_API_BASE.lower()

    # SiliconFlow (硅基流动)
    if "siliconflow" in api_base:
        # Free models: Qwen/Qwen2.5-7B-Instruct (recommended)
        return "Qwen/Qwen2.5-7B-Instruct"

    # DeepSeek
    if "deepseek" in api_base:
        return "deepseek-chat"

    # OpenAI
    if "openai.com" in api_base:
        return "gpt-3.5-turbo"

    # Default fallback
    return "gpt-3.5-turbo"


def get_embedding_model() -> str | None:
    """Auto-detect embedding model based on API base URL.

    Returns:
        Embedding model name string or None to use default
    """
    # If explicitly set and not empty, use it
    if settings.OPENAI_EMBEDDING_MODEL and settings.OPENAI_EMBEDDING_MODEL != "auto":
        return settings.OPENAI_EMBEDDING_MODEL

    # If set to "auto" or empty, try to auto-detect
    api_base = settings.OPENAI_API_BASE.lower()
    
    # SiliconFlow - use recommended models
    if "siliconflow" in api_base:
        # Default to Chinese model for SiliconFlow
        return "BAAI/bge-large-zh-v1.5"
    
    # OpenAI
    if "openai.com" in api_base:
        return "text-embedding-3-small"

    # Default fallback
    return "text-embedding-3-small"
