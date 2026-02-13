"""Configuration management for Thordata RAG Pipeline."""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-driven configuration for the RAG pipeline."""

    # Thordata credentials
    THORDATA_SCRAPER_TOKEN: str
    THORDATA_PUBLIC_TOKEN: Optional[str] = None
    THORDATA_PUBLIC_KEY: Optional[str] = None

    # LLM configuration
    OPENAI_API_KEY: str
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    # Model selection: auto-detect based on API base
    # For SiliconFlow: Qwen/Qwen2.5-7B-Instruct, Qwen/Qwen2.5-14B-Instruct, etc.
    # For OpenAI: gpt-3.5-turbo, gpt-4, etc.
    OPENAI_MODEL: str = "auto"  # Will auto-detect based on API_BASE
    OPENAI_EMBEDDING_MODEL: str = "auto"  # Will auto-detect based on API_BASE
    OPENAI_TEMPERATURE: float = 0.3
    OPENAI_MAX_TOKENS: int = 2000

    # Vector store configuration
    DB_PATH: str = "./data/chroma_db"
    COLLECTION_NAME: str = "thordata_rag"
    CHUNK_SIZE: int = 400  # Optimized for SiliconFlow embedding API (512 token limit)
    CHUNK_OVERLAP: int = 50  # Reduced overlap for smaller chunks

    # Scraping configuration
    SCRAPING_TIMEOUT: int = 60
    SCRAPING_MAX_RETRIES: int = 3
    SCRAPING_RETRY_BACKOFF: float = 2.0
    ENABLE_JS_RENDER: bool = True
    DEFAULT_COUNTRY: Optional[str] = None

    # Performance and caching
    ENABLE_CACHE: bool = True
    CACHE_TTL: int = 3600  # 1 hour
    MAX_CONTENT_LENGTH: int = 50000  # Max chars to process

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()


# Convenience instance for modules that import `settings` directly
settings: Settings = get_settings()
