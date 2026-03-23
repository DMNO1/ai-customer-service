"""
Web Scraper Service for AI Customer Service System
Handles extracting content from URLs using compliant methods
"""

import logging
from typing import Optional
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self, delay: float = 1.0):
        """
        Initialize the Web Scraper Service
        :param delay: Delay between requests in seconds to be respectful to servers
        """
        self.delay = delay
        self.session = requests.Session()
        # Set a user agent to be respectful
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; AI-Customer-Service/1.0; +https://example.com/bot-info)'
        })
        logger.info("WebScraper initialized successfully")

    def scrape_url(self, url: str) -> Optional[str]:
        """
        Scrape content from a URL
        :param url: URL to scrape
        :return: Extracted content or None if failed
        """
        try:
            logger.info(f"Scraping URL: {url}")
            
            # Validate URL format
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError(f"Invalid URL format: {url}")
            
            # Add delay to be respectful to the server
            time.sleep(self.delay)
            
            # Make request
            response = self.session.get(url, timeout=10)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            # Extract content
            content = self.extract_content(response.text, url)
            
            logger.info(f"Successfully scraped URL: {url}")
            return content
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error scraping URL {url}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error scraping URL {url}: {str(e)}")
            return None

    def extract_content(self, html: str, base_url: str = "") -> str:
        """
        Extract main content from HTML
        :param html: HTML content to extract from
        :param base_url: Base URL for resolving relative links
        :return: Extracted text content
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                script.decompose()
            
            # Try to find main content areas
            main_content = None
            
            # Look for main tag
            main_content = soup.find('main')
            if not main_content:
                # Look for article tag
                main_content = soup.find('article')
            if not main_content:
                # Look for div with common content classes
                for cls in ['content', 'main-content', 'post-content', 'entry-content', 'article-body']:
                    main_content = soup.find(['div', 'section'], class_=re.compile(cls, re.I))
                    if main_content:
                        break
            if not main_content:
                # Fallback to body
                main_content = soup.find('body')
            
            if main_content:
                # Extract text from main content
                text = main_content.get_text(separator='\n')
                
                # Clean up text
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = '\n'.join(chunk for chunk in chunks if chunk)
                
                return text
            else:
                # If no main content found, extract from the whole document
                text = soup.get_text(separator='\n')
                
                # Clean up text
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = '\n'.join(chunk for chunk in chunks if chunk)
                
                return text
                
        except Exception as e:
            logger.error(f"Error extracting content from HTML: {str(e)}")
            # Fallback: return plain text if extraction fails
            soup = BeautifulSoup(html, 'html.parser')
            return soup.get_text()

# Example usage and testing
if __name__ == "__main__":
    scraper = WebScraper()
    
    # Example usage (uncomment to test with actual URLs):
    # content = scraper.scrape_url("https://example.com")
    # print(content)