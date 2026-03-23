"""
Web Scraper for AI Customer Service System
Handles scraping and extracting content from URLs
"""

import logging
import asyncio
from typing import Optional
from urllib.parse import urljoin, urlparse
import re

try:
    from playwright.async_api import async_playwright
    from bs4 import BeautifulSoup
    import requests
except ImportError as e:
    logging.error(f"Missing required packages for web scraping: {e}")
    raise


class WebScraper:
    """
    Class for scraping web content
    """

    def __init__(self, timeout: int = 30):
        """
        Initialize the web scraper
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        logging.info("WebScraper initialized")

    async def scrape_url(self, url: str) -> str:
        """
        Scrape content from a URL using Playwright for JavaScript rendering
        
        Args:
            url: URL to scrape
            
        Returns:
            Extracted text content from the webpage
        """
        try:
            async with async_playwright() as p:
                # Launch browser (use chromium)
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Set timeout
                page.set_default_timeout(self.timeout * 1000)
                
                # Navigate to the page
                await page.goto(url, wait_until="networkidle")
                
                # Wait for additional content to load
                await page.wait_for_timeout(2000)
                
                # Get the HTML content
                html_content = await page.content()
                
                # Close browser
                await browser.close()
                
                # Extract text content from HTML
                text_content = self.extract_content(html_content)
                
                logging.info(f"Successfully scraped URL: {url}, extracted {len(text_content)} characters")
                return text_content
                
        except Exception as e:
            logging.error(f"Error scraping URL {url} with Playwright: {str(e)}")
            # Fallback to requests + BeautifulSoup
            return await self.scrape_url_fallback(url)

    async def scrape_url_fallback(self, url: str) -> str:
        """
        Fallback method to scrape content using requests and BeautifulSoup
        
        Args:
            url: URL to scrape
            
        Returns:
            Extracted text content from the webpage
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            text_content = self.extract_content(response.text)
            
            logging.info(f"Fallback scraping successful for URL: {url}")
            return text_content
            
        except Exception as e:
            logging.error(f"Error in fallback scraping for URL {url}: {str(e)}")
            raise

    def extract_content(self, html: str) -> str:
        """
        Extract meaningful content from HTML, removing ads, navigation, etc.
        
        Args:
            html: HTML content to extract text from
            
        Returns:
            Clean text content
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove unwanted elements
            for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement', 'ads']):
                tag.decompose()
            
            # Try to find main content areas
            main_content = None
            
            # Look for main tag first
            main_content = soup.find('main')
            if not main_content:
                # Look for article tag
                main_content = soup.find('article')
            if not main_content:
                # Look for content in specific classes
                for class_name in ['content', 'main-content', 'post-content', 'entry-content', 'article-body']:
                    main_content = soup.find(class_=class_name)
                    if main_content:
                        break
            if not main_content:
                # Use the body as fallback
                main_content = soup.find('body')
            if not main_content:
                # Use the entire soup as last resort
                main_content = soup
            
            # Extract text
            text = main_content.get_text(separator='\n')
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            
            return text
            
        except Exception as e:
            logging.error(f"Error extracting content from HTML: {str(e)}")
            # Return basic text extraction as fallback
            soup = BeautifulSoup(html, 'html.parser')
            return soup.get_text(separator=' ').strip()

    async def extract_metadata(self, url: str) -> dict:
        """
        Extract metadata (title, description, etc.) from a URL
        
        Args:
            url: URL to extract metadata from
            
        Returns:
            Dictionary containing metadata
        """
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(url, wait_until="networkidle")
                
                # Extract metadata
                title = await page.title()
                description = await page.evaluate('() => { const el = document.querySelector("meta[name=\'description\']") || document.querySelector("meta[property=\'og:description\']"); return el ? el.content : ""; }')
                og_title = await page.evaluate('() => { const el = document.querySelector("meta[property=\'og:title\']"); return el ? el.content : ""; }')
                
                await browser.close()
                
                metadata = {
                    'title': title or og_title,
                    'description': description,
                    'url': url
                }
                
                return metadata
                
        except Exception as e:
            logging.error(f"Error extracting metadata from {url}: {str(e)}")
            return {'url': url}


# Initialize logging
logging.basicConfig(level=logging.INFO)


async def test_web_scraper():
    """
    Test function for the web scraper
    """
    print("Testing Web Scraper...")
    
    scraper = WebScraper()
    
    # Example usage would go here
    print("WebScraper initialized successfully")


if __name__ == "__main__":
    asyncio.run(test_web_scraper())