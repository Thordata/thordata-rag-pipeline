# 📚 Thordata RAG Pipeline

A production-ready pipeline to scrape web pages, clean the HTML, and convert it to Markdown for RAG (Retrieval-Augmented Generation) knowledge bases.

## Features
- **Web Unlocker**: Uses Thordata to bypass anti-bots and render JavaScript.
- **HTML Cleaning**: Removes noise (ads, navs) using BeautifulSoup.
- **Markdown Export**: Formats text specifically for LLM ingestion.

## Usage
```bash
pip install -r requirements.txt
python rag_pipeline.py --url "https://openai.com/research" --output "data/kb.md"
```
