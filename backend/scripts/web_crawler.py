"""
Web Crawler
安全地抓取指定网站内容（需遵守robots.txt）。
"""

import requests
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin, urlparse
import time
from typing import Dict, List, Optional

class WebCrawler:
    def __init__(self, delay: float = 1.0, user_agent: str = "AI-Customer-Service-Bot"):
        self.delay = delay
        self.user_agent = user_agent
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
    
    def can_fetch(self, url: str) -> bool:
        """
        检查是否允许抓取指定URL（根据robots.txt）。
        
        Args:
            url: 要检查的URL。
            
        Returns:
            如果允许抓取则返回True，否则返回False。
        """
        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            return rp.can_fetch(self.user_agent, url)
        except Exception as e:
            print(f"Error checking robots.txt for {url}: {e}")
            # 如果无法获取robots.txt，保守起见返回False
            return False
    
    def crawl_page(self, url: str) -> Optional[Dict[str, str]]:
        """
        抓取单个网页的内容。
        
        Args:
            url: 要抓取的网页URL。
            
        Returns:
            包含标题和正文的字典，如果抓取失败则返回None。
        """
        if not self.can_fetch(url):
            print(f"Robots.txt disallows crawling: {url}")
            return None
        
        try:
            time.sleep(self.delay)  # 遵守抓取延迟
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 提取标题
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ""
            
            # 移除脚本和样式标签
            for script in soup(["script", "style"]):
                script.decompose()
            
            # 提取正文文本
            body_text = soup.get_text()
            # 清理多余的空白字符
            lines = (line.strip() for line in body_text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            body_text = ' '.join(chunk for chunk in chunks if chunk)
            
            return {
                "title": title_text,
                "content": body_text,
                "url": url
            }
        except Exception as e:
            print(f"Error crawling {url}: {e}")
            return None

# 用于测试的主函数
if __name__ == "__main__":
    crawler = WebCrawler()
    test_url = "https://example.com"
    result = crawler.crawl_page(test_url)
    if result:
        print(f"Title: {result['title']}")
        print(f"Content preview: {result['content'][:200]}...")
    else:
        print("Failed to crawl the page.")