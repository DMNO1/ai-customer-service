"""
网页抓取服务 - 提取网页主要内容
支持 JavaScript 渲染和非渲染页面
"""

import asyncio
from typing import Optional, Dict, Any
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from readability import Document as ReadabilityDocument
from playwright.async_api import async_playwright

from app.core.exceptions import AppException
import structlog

logger = structlog.get_logger()

class WebScraper:
    """网页抓取器 - 支持静态和动态页面"""

    def __init__(self, use_playwright: bool = True, timeout: int = 30):
        """
        初始化抓取器

        Args:
            use_playwright: 是否使用 Playwright 处理 JS 渲染
            timeout: 超时时间（秒）
        """
        self.use_playwright = use_playwright
        self.timeout = timeout
        self._playwright = None

    async def __aenter__(self):
        if self.use_playwright:
            self._playwright = await async_playwright().start()
            self.browser = await self._playwright.chromium.launch(headless=True)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._playwright:
            await self.browser.close()
            await self._playwright.stop()

    async def scrape_url(self, url: str, js_render: bool = None) -> Dict[str, Any]:
        """
        抓取网页内容

        Args:
            url: 目标网址
            js_render: 是否强制使用 JS 渲染（None = 自动判断）

        Returns:
            Dict with keys: title, content, url, html, text
        """
        if not url.startswith(('http://', 'https://')):
            raise AppException(f"无效的URL: {url}")

        try:
            if js_render is None:
                # 自动判断是否需要 JS 渲染
                js_render = await self._should_use_js(url)

            if js_render and self.use_playwright:
                return await self._scrape_with_playwright(url)
            else:
                return await self._scrape_with_requests(url)

        except Exception as e:
            logger.error("scrape_url_failed", url=url, error=str(e))
            raise AppException(f"网页抓取失败: {str(e)}", details={"url": url})

    async def _should_use_js(self, url: str, max_redirects: int = 5) -> bool:
        """
        判断网页是否需要 JS 渲染
        简单启发式：检查常见的 SPA 框架特征
        """
        try:
            async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
                resp = await client.get(url)
                html = resp.text

                # 检查常见的 JS 框架特征
                js_indicators = [
                    'id="app"', 'id="root"', 'data-reactroot',
                    'ng-app', 'v-app', 'ember-application',
                    'window.__INITIAL_STATE__', 'window.__PRELOADED_STATE__'
                ]

                soup = BeautifulSoup(html, 'html.parser')
                text = soup.get_text()

                # 如果页面内容极少，可能依赖 JS 渲染
                if len(text.strip()) < 1000:
                    for indicator in js_indicators:
                        if indicator in html:
                            logger.info("js_render_detected", url=url, indicator=indicator)
                            return True

            return False

        except Exception:
            return False  # 出错时使用普通抓取

    async def _scrape_with_requests(self, url: str) -> Dict[str, Any]:
        """使用 httpx + BeautifulSoup 抓取"""
        async with httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()

            # 使用 Readability 提取主要内容
            doc = ReadabilityDocument(resp.text)
            content = doc.summary()

            # BeautifulSoup 清理
            soup = BeautifulSoup(content, 'html.parser')
            text = soup.get_text(separator='\n', strip=True)

            return {
                'title': doc.title(),
                'content': content,
                'url': str(resp.url),
                'html': resp.text,
                'text': self._clean_text(text),
                'method': 'requests'
            }

    async def _scrape_with_playwright(self, url: str) -> Dict[str, Any]:
        """使用 Playwright 抓取 JS 渲染页面"""
        if not self._playwright:
            raise AppException("Playwright 未初始化")

        page = await self.browser.new_page(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )

        try:
            await page.goto(url, wait_until='networkidle', timeout=self.timeout * 1000)
            await page.wait_for_timeout(2000)  # 等待动态内容加载

            html = await page.content()
            doc = ReadabilityDocument(html)
            content = doc.summary()

            soup = BeautifulSoup(content, 'html.parser')
            text = soup.get_text(separator='\n', strip=True)

            return {
                'title': doc.title(),
                'content': content,
                'url': page.url,
                'html': html,
                'text': self._clean_text(text),
                'method': 'playwright'
            }

        finally:
            await page.close()

    @staticmethod
    def _clean_text(text: str) -> str:
        """清理提取的文本"""
        lines = text.split('\n')
        cleaned = []

        for line in lines:
            line = line.strip()
            if line:
                cleaned.append(line)

        # 移除过短且重复的行
        result = []
        prev = ""
        for line in cleaned:
            if len(line) < 5 and line == prev:
                continue
            result.append(line)
            prev = line

        return "\n".join(result)

    @staticmethod
    def validate_url(url: str) -> bool:
        """验证 URL 有效性"""
        try:
            result = urlparse(url)
            return all([result.scheme in ['http', 'https'], result.netloc])
        except:
            return False


# 便捷函数
async def scrape_url(url: str, use_js: bool = None) -> Dict[str, Any]:
    """快捷抓取函数"""
    async with WebScraper(use_playwright=True) as scraper:
        return await scraper.scrape_url(url, js_render=use_js)
