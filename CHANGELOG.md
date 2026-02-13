# Changelog

## [2.0.0] - 2025-02-13

### Added
- Automatic spider discovery from Thordata SDK (107+ spiders)
- Multi-provider LLM support with auto-detection (SiliconFlow, OpenAI, DeepSeek)
- Batch processing with async concurrency
- Performance monitoring utilities
- Quick start script for simplified usage
- Windows console encoding fixes
- Comprehensive error handling
- Batch embedding processing (30 chunks per batch for API limits)
- Token-aware chunking (400 chars optimized for 512 token limit)

### Changed
- Upgraded to Thordata SDK 1.8.4+
- Refactored to async/await architecture
- Improved error messages and logging
- Simplified user experience
- Enhanced documentation (bilingual)
- Optimized chunk size (400 chars) for SiliconFlow embedding API
- Reduced chunk overlap (50 chars) for better performance

### Fixed
- Windows console encoding issues
- Task error handling and reporting
- Import errors in spider discovery
- Configuration loading
- Embedding model configuration for SiliconFlow
- Batch size limits (API 512 token limit per input)
- LangChain text splitter import (using langchain-text-splitters)

### Removed
- Oxylabs comparison section (Thordata brand focus)

### Tested & Verified
- ✅ Full RAG pipeline with Wikipedia content
- ✅ Embedding API integration (BAAI/bge-large-zh-v1.5)
- ✅ Vector store operations (ChromaDB)
- ✅ LLM query generation (Qwen/Qwen2.5-7B-Instruct)
- ✅ Batch processing for large documents
