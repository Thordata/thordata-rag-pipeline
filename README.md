# Thordata RAG Pipeline

<div align="center">

<img src="https://img.shields.io/badge/Thordata-Official-blue?style=for-the-badge" alt="Thordata Logo">

**Production-grade RAG ingestion pipeline. Turn ANY website into structured AI knowledge.**  
*Smart Routing • Hybrid Scraping • 45+ Supported Platforms*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

</div>

---

## 💡 What is this?

This is a flagship implementation of a **"Universal Web Reader"** for AI Agents. It solves the hardest part of RAG (Retrieval-Augmented Generation): **Getting clean, structured data from complex websites.**

Unlike standard scrapers that break on dynamic sites, this pipeline uses **Thordata's Smart Routing Architecture**:

1.  **🕵️ Smart Router**: Automatically detects the URL type (Amazon, YouTube, Google Maps, etc.).
2.  **⚡ Specialized Ingestors**: Dispatches tasks to **45+ specialized spiders** (e.g., `amazon_product`, `tiktok_video`) to fetch **structured JSON**.
3.  **🌐 Universal Fallback**: If no specialized tool matches (or if it fails), it falls back to a Headless Browser cluster to render the page and extract **Markdown**.
4.  **🧠 Semantic Analysis**: Feeds the cleaned data into an LLM (DeepSeek/Qwen/GPT-4o) for instant insight generation.

---

## 🚀 Supported Platforms (Auto-Detected)

Just paste a URL, and the pipeline selects the best strategy:

| Platform | Supported URLs | Data Type |
| :--- | :--- | :--- |
| **Amazon** | Product (`/dp/`), Search (`/s?k=`), Reviews, Seller | JSON (Price, Rating, ASIN) |
| **Google** | Maps, Shopping, Play Store (App & Reviews) | JSON (Business Info, App Stats) |
| **Social** | YouTube (Video/Channel), TikTok (Video/Profile/Shop) | JSON (Views, Likes, Metadata) |
| **Social** | Instagram, Facebook, Twitter (X), LinkedIn (Company/Job) | JSON (Post content, Profile info) |
| **Others** | Reddit, GitHub, Zillow, Booking.com, Yelp | JSON (Structured Data) |
| **General** | Any other website (TechCrunch, Wikipedia, etc.) | Markdown (Full Page Text) |

---

## 🛠️ Quick Start

### 1. Prerequisites
*   Python 3.10+
*   [Thordata API Tokens](https://www.thordata.com/)
*   OpenAI-compatible API Key (DeepSeek, SiliconFlow, or OpenAI)

### 2. Installation
```bash
git clone https://github.com/Thordata/thordata-rag-pipeline.git
cd thordata-rag-pipeline
pip install -r requirements.txt
```

### 3. Configuration
Copy `.env.example` to `.env` and fill in your keys:
```ini
THORDATA_SCRAPER_TOKEN=your_token
THORDATA_PUBLIC_TOKEN=your_public_token
THORDATA_PUBLIC_KEY=your_public_key

OPENAI_API_KEY=sk-xxxx
OPENAI_API_BASE=https://api.siliconflow.cn/v1  # Example for SiliconFlow
```

### 4. Run Analysis

**Analyze an Amazon Product:**
```bash
python main.py --url "https://www.amazon.com/dp/B0D54MM6QD" --question "What are the pros and cons?"
```

**Analyze a Google Maps Place (Detailed):**
```bash
python main.py --url 'https://www.google.com/maps/place/Pizza+Inn+Magdeburg/data=!4m7!3m6!1s0x47a5f50c083530a3:0xfdba8746b538141!8m2!3d52.1263086!4d11.6094743!16s%2Fg%2F11kqmtk3dt!19sChIJozA1CAz1pUcRQYFTa3So2w8?authuser=0&hl=en&rclk=1' --question "Where is this place located?"
```

**Analyze a Google Play App:**
```bash
python main.py --url "https://play.google.com/store/apps/details?id=com.whatsapp" --question "What is the rating?"
```

**Analyze Any Website (Universal Mode):**
```bash
python main.py --url "https://techcrunch.com/..." --question "Summarize this article."
```

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
