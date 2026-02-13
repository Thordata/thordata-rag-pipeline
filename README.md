# ⚡ Thordata RAG Pipeline

<div align="center">

**Intelligent Web Scraping & Question Answering System**  
**智能网页抓取与问答系统**

*Powered by Thordata SDK + LangChain + ChromaDB*  
*基于 Thordata SDK + LangChain + ChromaDB 构建*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Thordata SDK](https://img.shields.io/badge/Thordata%20SDK-1.8.4%2B-green)](https://github.com/Thordata/thordata-python-sdk)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

</div>

---

## 📖 Overview | 概述

Thordata RAG Pipeline is a production-ready system that combines intelligent web scraping with Retrieval-Augmented Generation (RAG) capabilities. It automatically scrapes content from any URL, stores it in a vector database, and enables natural language question answering over the collected knowledge.

**Thordata RAG Pipeline** 是一个生产就绪的系统，结合了智能网页抓取和检索增强生成（RAG）能力。它可以自动从任何 URL 抓取内容，存储到向量数据库中，并支持对收集的知识进行自然语言问答。

### What is RAG? | 什么是 RAG？

**RAG** (Retrieval-Augmented Generation) = **检索增强生成**

Think of it as a super assistant that:
- Takes a URL, "reads" the webpage, and memorizes important content
- Organizes and stores the content in a "knowledge base"
- Answers your questions based on the stored knowledge

**RAG** 就像一个超级助手：
- 你给它一个网址，它去"看"这个网页，把重要内容记下来
- 它把看到的内容整理好，存到一个"知识库"里
- 之后你问它任何关于这些内容的问题，它都能从"知识库"里找到答案告诉你

**Why RAG? | 为什么需要 RAG？**
- AI models have limited knowledge and may be outdated
- RAG allows AI to answer questions about the latest web content
- Like giving AI a "real-time updated encyclopedia"

**为什么需要 RAG？**
- AI 模型本身的知识有限，而且可能过时
- 通过 RAG，可以让 AI 回答关于最新网页内容的问题
- 就像给 AI 配了一个"实时更新的百科全书"

### Key Highlights | 核心亮点

- ✅ **107+ Auto-Discovered Spiders | 107+ 自动发现爬虫** - No manual configuration needed | 无需手动配置
- ✅ **Free LLM Support | 免费 LLM 支持** - Works with SiliconFlow free models | 支持硅基流动免费模型  
- ✅ **One-Command Usage | 一键使用** - `quick_start.py` for instant results | `quick_start.py` 即时结果
- ✅ **Production Ready | 生产就绪** - Async, cached, monitored | 异步、缓存、监控
- ✅ **Smart Routing | 智能路由** - Automatically selects best scraping strategy | 自动选择最佳抓取策略

---

## ✨ Key Features | 核心特性

### 🧠 Smart Routing | 智能路由
Automatically selects the best scraping strategy (specialized spiders vs. universal scraper)  
自动选择最佳抓取策略（专业爬虫 vs 通用爬虫）

**How it works | 工作原理：**
- Analyzes URL to determine website type
- Uses specialized spiders for known sites (Amazon, YouTube, etc.)
- Falls back to universal scraper for unknown sites
- 分析网址判断网站类型
- 对已知网站使用专业爬虫（Amazon、YouTube 等）
- 对未知网站使用通用爬虫

### 🕷️ 107+ Auto-Discovered Spiders | 107+ 自动发现爬虫
Automatically discovers and uses all available spiders from Thordata SDK  
自动发现并使用 Thordata SDK 中的所有可用爬虫

**Supported Platforms | 支持的平台：**
- **E-Commerce | 电商**: Amazon, Google Shopping, TikTok Shop
- **Social Media | 社交媒体**: YouTube, TikTok, Instagram, Facebook, Twitter, Reddit, LinkedIn
- **Maps & Stores | 地图和商店**: Google Maps, Google Play Store
- **Code Platforms | 代码平台**: GitHub
- **Universal | 通用**: Any other website

### 🌐 Universal Scraper | 通用爬虫
Fallback to headless browser scraping for any website  
对任何网站的后备无头浏览器抓取

### 📚 Vector Storage | 向量存储
ChromaDB integration for semantic search  
ChromaDB 集成用于语义搜索

**What is Vector Store? | 什么是向量存储？**
- Converts text into numerical vectors (e.g., [0.1, 0.5, -0.3, ...])
- Similar texts have similar vectors
- Enables fast similarity search
- 把文字转换成数字列表（向量）
- 相似的文字会有相似的数字列表
- 支持快速相似度搜索

### 💬 RAG Q&A | RAG 问答
Ask questions about scraped content using LLMs  
使用大语言模型对抓取内容进行问答

### ⚡ Async-First | 异步优先
Built on async/await for high performance  
基于 async/await 构建，性能优异

### 💾 Intelligent Caching | 智能缓存
In-memory cache to avoid redundant scraping  
内存缓存避免重复抓取

### 🔄 Batch Processing | 批量处理
Process multiple URLs concurrently  
并发处理多个 URL

### 🔌 Multi-Provider LLM Support | 多提供商 LLM 支持
Auto-detects models for SiliconFlow, OpenAI, DeepSeek, etc.  
自动检测硅基流动、OpenAI、DeepSeek 等模型的配置

**Recommended Free Models | 推荐的免费模型：**
- **LLM**: `Qwen/Qwen2.5-7B-Instruct` (via SiliconFlow)
- **Embedding**: `BAAI/bge-large-zh-v1.5` (via SiliconFlow)

### ✅ Production Tested | 生产测试
Fully tested and verified with real APIs  
已使用真实 API 完整测试验证

---

## 🚀 Quick Start | 快速开始

### Prerequisites | 前置要求

- Python 3.10 or higher | Python 3.10 或更高版本
- Thordata API credentials | Thordata API 凭证
- LLM API key (SiliconFlow recommended for free models) | LLM API 密钥（推荐硅基流动免费模型）

### Installation | 安装

#### 1. Clone the repository | 克隆仓库

```bash
git clone https://github.com/Thordata/thordata-rag-pipeline.git
cd thordata-rag-pipeline
```

#### 2. Install dependencies | 安装依赖

```bash
pip install -r requirements.txt
```

#### 3. Verify setup | 验证安装

```bash
python check_setup.py
```

You should see "Setup complete! You can now use the pipeline."  
你应该看到 "Setup complete! You can now use the pipeline."

#### 4. Configure credentials | 配置凭证

Copy `.env.example` to `.env` and fill in your credentials:  
复制 `.env.example` 到 `.env` 并填写您的凭证：

```bash
cp .env.example .env
# Edit .env with your credentials
```

**Required configuration | 必需配置：**

```ini
# Thordata Credentials | Thordata 凭证
THORDATA_SCRAPER_TOKEN=your_token_here
THORDATA_PUBLIC_TOKEN=your_token_here
THORDATA_PUBLIC_KEY=your_key_here

# LLM Configuration | LLM 配置
# For SiliconFlow (Free) | 硅基流动（免费）
OPENAI_API_KEY=your_siliconflow_api_key
OPENAI_API_BASE=https://api.siliconflow.cn/v1
OPENAI_MODEL=Qwen/Qwen2.5-7B-Instruct
OPENAI_EMBEDDING_MODEL=BAAI/bge-large-zh-v1.5
```

**Where to get credentials | 如何获取凭证：**
- **Thordata**: Get from [Thordata website](https://thordata.com) | 从 [Thordata 官网](https://thordata.com) 获取
- **SiliconFlow**: Get free API key from [SiliconFlow](https://siliconflow.cn) | 从 [硅基流动](https://siliconflow.cn) 获取免费 API 密钥

---

## 📚 Usage | 使用方法

### Method 1: Quick Start (Simplest) | 方法一：快速开始（最简单）

One command to scrape and answer:  
一条命令完成抓取和回答：

```bash
python quick_start.py "https://example.com" "What is this website about?"
python quick_start.py "https://example.com" "这个网站讲什么？"
```

**What it does | 系统会：**
1. Scrape the webpage | 抓取网页内容
2. Store in vector database | 存储到向量数据库
3. Answer your question | 回答你的问题

### Method 2: Full Pipeline | 方法二：完整流程

#### Scrape and Answer | 抓取并回答问题

```bash
python main.py --url "https://example.com" --question "What is this about?"
python main.py --url "https://example.com" --question "这个网站讲什么？"
```

#### Ingest Only | 仅抓取

```bash
python main.py --url "https://example.com" --ingest-only
```

**Use cases | 适用场景：**
- Collect content first, ask questions later | 想先收集内容，稍后再问问题
- Batch scraping multiple websites | 批量抓取多个网站

#### Query Only | 仅查询

```bash
python main.py --question "What did we learn about Python?" --query-only
python main.py --question "之前抓取的内容中，Python 的特点是什么？" --query-only
```

**Use cases | 适用场景：**
- Already scraped content | 已经抓取过内容
- Query existing knowledge base | 想查询之前存储的知识

#### Batch Processing | 批量处理

```bash
python main.py --urls "https://example.com,https://another.com,https://third.com" --ingest-only
```

**Note | 注意**: URLs separated by commas, no spaces | 网址之间用逗号分隔，不要有空格

#### Advanced Options | 高级选项

```bash
# Disable cache | 禁用缓存
python main.py --url "https://example.com" --no-cache

# Specify number of documents to retrieve (default: 5) | 指定检索的文档数量（默认5个）
python main.py --url "https://example.com" --question "Question" --k 10

# Clear cache | 清除缓存
python main.py --url "https://example.com" --clear-cache
```

---

## 🔧 How It Works | 工作原理

### Complete Pipeline | 完整流程

```
1. Input URL and question | 输入网址和问题
   ↓
2. Smart routing selects scraping method | 智能路由选择抓取方式
   ├─ Specialized spider (Amazon, YouTube, etc.) | 专业爬虫
   └─ Universal scraper (other websites) | 通用爬虫
   ↓
3. Scrape webpage content | 抓取网页内容
   ↓
4. Chunk content (split into segments) | 内容分块
   ↓
5. Convert to vectors (using embedding model) | 转换为向量
   ↓
6. Store in vector database | 存储到向量数据库
   ↓
7. Search relevant content (vector similarity) | 搜索相关内容
   ↓
8. Generate answer (using LLM) | AI 生成答案
   ↓
9. Return answer | 返回答案
```

### Key Components | 核心组件

#### 1. Smart Router | 智能路由
- Analyzes URL patterns | 分析网址模式
- Selects best scraping strategy | 选择最佳抓取策略
- Falls back automatically | 自动降级处理

#### 2. Document Chunker | 文档分块
- Splits long content into manageable chunks | 将长内容分割成可管理的块
- Optimized chunk size: 400 characters (for 512 token limit) | 优化块大小：400 字符（适配 512 token 限制）
- Overlap: 50 characters (prevents information loss) | 重叠：50 字符（避免信息丢失）

#### 3. Vector Store | 向量存储
- **Embedding Model**: `BAAI/bge-large-zh-v1.5` (Chinese-optimized) | 中文优化模型
- **Database**: ChromaDB (local storage) | 本地存储
- **Vector Dimension**: 1024 | 向量维度：1024

#### 4. LLM Query | LLM 查询
- **Model**: `Qwen/Qwen2.5-7B-Instruct` (Free via SiliconFlow) | 免费模型（通过硅基流动）
- **Process**: Retrieves relevant chunks → Generates answer | 检索相关块 → 生成答案

---

## 📊 Performance | 性能指标

- **Scraping Speed**: ~10-15 seconds (large pages) | 抓取速度：~10-15 秒（大网页）
- **Embedding Speed**: ~0.5 seconds per batch (30 chunks) | 向量化速度：~0.5 秒/批次（30 个文档块）
- **LLM Response**: ~1-2 seconds | AI 响应：~1-2 秒
- **Total Pipeline**: ~15-20 seconds (full RAG cycle) | 完整流程：~15-20 秒

---

## ❓ FAQ | 常见问题

### 1. Why do I need Thordata credentials? | 为什么需要 Thordata 密钥？

**Answer | 答**：Thordata provides professional web scraping services:
- Anti-bot bypass | 反爬虫绕过
- JavaScript rendering | JavaScript 渲染
- IP proxy | IP 代理
- 107+ specialized spiders | 107+ 专业爬虫

These services require paid usage (pay-per-use).  
这些服务需要付费使用（按使用量计费）。

### 2. Why do I need LLM API key? | 为什么需要 LLM API 密钥？

**Answer | 答**：AI models require computational resources. Even with free models (like SiliconFlow), you need:
- API key for authentication | API 密钥验证身份
- Server resources to process requests | 服务器资源处理请求

**Good news | 好消息**：SiliconFlow provides free quota, sufficient for daily use.  
硅基流动提供免费额度，足够日常使用。

### 3. Where is data stored? | 数据存储在哪里？

**Answer | 答**：
- **Vector Database**: `./data/chroma_db/` (local folder) | 本地文件夹
- **Cache**: In memory (cleared when program closes) | 内存中（程序关闭后消失）
- **Original Content**: Not saved, only processed vectors | 不保存，只保存处理后的向量

**⚠️ Important | 重要**：`.env` file contains keys - **DO NOT** upload to GitHub!  
`.env` 文件包含密钥，**不要**上传到 GitHub！

### 4. Which websites can I scrape? | 可以抓取哪些网站？

**Answer | 答**：
- **Specialized Support**: Amazon, YouTube, TikTok, Instagram, etc. (107+ websites) | 107+ 种网站
- **Universal Support**: Any publicly accessible website | 任何可公开访问的网站

**Limitations | 限制**：
- Website must be publicly accessible | 需要网站可公开访问
- Some websites may have access restrictions | 某些网站可能有访问限制
- Scraping speed depends on website response time | 抓取速度取决于网站响应速度

### 5. Does scraped content expire? | 抓取的内容会过期吗？

**Answer | 答**：
- Content in vector database does not auto-update | 向量数据库中的内容不会自动更新
- If webpage content updates, re-scrape is needed | 如果网页内容更新了，需要重新抓取
- You can periodically run scraping commands to update | 可以定期运行抓取命令更新内容

### 6. How long can a webpage be? | 可以处理多长的网页？

**Answer | 答**：
- Default: Max 50,000 characters | 默认最多处理 50,000 个字符
- Excess content will be truncated | 超过部分会被截断
- Can modify `MAX_CONTENT_LENGTH` in `.env` | 可以在 `.env` 中修改 `MAX_CONTENT_LENGTH`

### 7. Why are answers inaccurate? | 为什么回答不准确？

**Possible reasons | 可能原因**：
1. **Insufficient scraped content**: Too little content or scraping failed | 抓取的内容不够
2. **Vague question**: Question too broad | 问题不够具体
3. **Content not in knowledge base**: What you're asking wasn't scraped | 相关内容不在知识库

**Solutions | 解决方法**：
- Check scraped content length (should be > 200 chars) | 检查抓取的内容长度
- Make questions specific and clear | 问题要具体明确
- Ensure relevant webpages have been scraped | 确保相关网页已经被抓取

### 8. Can I process multiple URLs at once? | 可以同时处理多个网址吗？

**Answer | 答**：Yes! Use batch mode:  
可以！使用批量模式：

```bash
python main.py --urls "url1,url2,url3" --ingest-only
```

System processes concurrently for efficiency.  
系统会并发处理，提高效率。

### 9. How do I check stored content? | 如何查看存储了多少内容？

**Answer | 答**：After running commands, statistics are displayed:  
运行命令后，最后会显示统计信息：

```
[STATS]
  Documents in vector store: 222
  Cached items: 1
```

### 10. How do I clear stored content? | 如何清除存储的内容？

**Answer | 答**：
- Delete `./data/chroma_db/` folder | 删除 `./data/chroma_db/` 文件夹
- New database will be created automatically on next run | 重新运行程序会自动创建新的数据库

---

## 🛠️ Troubleshooting | 故障排除

### Embedding Model Issues | 嵌入模型问题

If you encounter "Model does not exist" errors with SiliconFlow:  
如果使用 SiliconFlow 时遇到"模型不存在"错误：

**Solution | 解决方案**：Set a valid embedding model in `.env`:  
在 `.env` 中设置有效的嵌入模型：

```ini
OPENAI_EMBEDDING_MODEL=BAAI/bge-large-zh-v1.5
```

### Import Errors | 导入错误

```bash
# Install missing dependencies | 安装缺失的依赖
pip install -r requirements.txt
```

### Configuration Errors | 配置错误

```bash
# Check your configuration | 检查配置
python check_setup.py
```

### Task Failures | 任务失败

- Check Thordata credentials in `.env` | 检查 `.env` 中的 Thordata 凭证
- Verify URL is accessible | 验证 URL 可访问
- Check task status in Thordata dashboard | 在 Thordata 仪表板中检查任务状态

---

## 📁 Project Structure | 项目结构

```
thordata-rag-pipeline/
├── .env.example          # Configuration template | 配置模板
├── .gitignore            # Git ignore file | Git 忽略文件
├── CHANGELOG.md          # Changelog | 变更日志
├── README.md             # This file | 本文件
├── requirements.txt      # Dependencies | 依赖列表
├── check_setup.py        # Setup verification | 环境检查脚本
├── main.py              # Main entry point | 主程序入口
├── quick_start.py       # Quick start script | 快速开始脚本
├── src/                 # Source code | 源代码
│   └── thordata_rag/
│       ├── core/        # Core configuration | 核心配置
│       ├── ingestors/   # Scraping modules | 抓取模块
│       └── processor/   # Processing modules | 处理模块
└── tests/               # Test files | 测试文件
```

---

## 🤝 Contributing | 贡献

Contributions are welcome! Please feel free to submit a Pull Request.  
欢迎贡献！请随时提交 Pull Request。

---

## 📄 License | 许可证

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.  
本项目采用 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。

---

## 🙏 Acknowledgments | 致谢

- [Thordata Python SDK](https://github.com/Thordata/thordata-python-sdk) - Web scraping infrastructure | 网页抓取基础设施
- [LangChain](https://github.com/langchain-ai/langchain) - LLM framework | LLM 框架
- [ChromaDB](https://www.trychroma.com/) - Vector database | 向量数据库
- [SiliconFlow](https://siliconflow.cn) - Free LLM API | 免费 LLM API

---

## 📞 Support | 支持

For detailed usage instructions, see the [Complete User Guide](../thordata-rag-pipeline-完整使用指南.md) (Chinese).  
详细使用说明，请参阅[完整使用指南](../thordata-rag-pipeline-完整使用指南.md)（中文）。

For issues and questions, please open an [Issue](https://github.com/Thordata/thordata-rag-pipeline/issues).  
如有问题和疑问，请提交 [Issue](https://github.com/Thordata/thordata-rag-pipeline/issues)。

---

<div align="center">

**Made with ❤️ by Thordata**  
**由 Thordata 用 ❤️ 制作**

</div>
