from thordata import ThordataClient
from markdownify import markdownify as md
from bs4 import BeautifulSoup
import logging

class UniversalIngestor:
    def __init__(self, scraper_token):
        self.client = ThordataClient(scraper_token=scraper_token)

    def _safe_clean_dom(self, html: str) -> str:
        """
        温和清洗：只移除绝对不需要的标签，保留 DOM 结构
        """
        soup = BeautifulSoup(html, "lxml")

        # 1. 移除绝对垃圾 (脚本、样式、元数据)
        for tag in soup(["script", "style", "noscript", "iframe", "meta", "link", "svg", "button", "input", "form"]):
            tag.decompose()

        # 2. 移除明确的导航和页脚区域 (但不要动 div，因为正文可能在 div 里)
        for tag in soup(["nav", "footer", "header", "aside"]):
            tag.decompose()

        # 3. 策略优化：如果存在 <article> 标签，优先提取 article
        # 这是绝大多数新闻/博客网站的标准正文容器
        article = soup.find("article")
        if article:
            return str(article)

        return str(soup.body) if soup.body else str(soup)

    def scrape_to_markdown(self, url: str, country: str = None) -> str:
        print(f"🌐 正在通过 Thordata 抓取网页: {url} (Region: {country or 'Auto'})...")
        try:
            # 1. SDK 请求
            kwargs = {
                "url": url,
                "js_render": True,
                "output_format": "html",
                "block_resources": "image,media", # 稍微放宽，font 有时影响布局判断
                "wait": 5000 
            }
            if country:
                kwargs["country"] = country

            raw_html = str(self.client.universal_scrape(**kwargs))
            
            # 2. 温和清洗
            cleaned_dom = self._safe_clean_dom(raw_html)

            # 3. 直接转 Markdown (不再依赖 Readability，因为它在现代 SPA 上容易失效)
            # heading_style="ATX" 保证生成 # 标题
            final_markdown = md(cleaned_dom, heading_style="ATX")
            
            # 4. 后处理：压缩连续空行
            import re
            final_markdown = re.sub(r'\n\s*\n', '\n\n', final_markdown)
            
            print(f"📝 提取策略: Safe Mode (Article/Body) | 内容长度: {len(final_markdown)} 字符")
            return final_markdown

        except Exception as e:
            return f"Universal Scraping Failed: {str(e)}"