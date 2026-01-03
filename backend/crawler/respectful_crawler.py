"""
Respectful crawling implementation with delays and robots.txt compliance.
"""
import requests
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
from typing import Dict, List, Optional
import time
import random
from datetime import datetime, timedelta
import os
import json
from pathlib import Path

from utils.logging_config import get_logger
from utils.error_handling import retry_crawl, CrawlError
from config.config import config

logger = get_logger("respectful_crawler")


class RespectfulCrawler:
    """
    Implements respectful crawling with delays and robots.txt compliance.
    """
    def __init__(self, base_url: str = None, delay: float = None, respect_robots: bool = True):
        """
        Initialize the respectful crawler.

        Args:
            base_url: Base URL of the website (defaults to config value)
            delay: Delay between requests in seconds (defaults to config value)
            respect_robots: Whether to respect robots.txt (default: True)
        """
        self.base_url = base_url or config.book_base_url
        self.delay = delay or config.crawl_delay
        self.respect_robots = respect_robots
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; BookCrawler/1.0; +http://example.com/bot)'
        })

        # Track request times to enforce delays
        self.last_request_time = None
        self.crawl_delay_from_robots = None

        # Robot parser cache
        self._robot_parsers: Dict[str, RobotFileParser] = {}

    def _get_robot_parser(self, base_url: str) -> RobotFileParser:
        """
        Get or create a robot parser for the given base URL.

        Args:
            base_url: Base URL to get robot parser for

        Returns:
            RobotFileParser: Robot parser instance for the domain
        """
        parsed_url = urlparse(base_url)
        domain = f"{parsed_url.scheme}://{parsed_url.netloc}"

        if domain not in self._robot_parsers:
            rp = RobotFileParser()
            robots_url = urljoin(domain, '/robots.txt')
            try:
                rp.set_url(robots_url)
                rp.read()
                logger.info(f"Loaded robots.txt from {robots_url}")
            except Exception as e:
                logger.warning(f"Could not load robots.txt from {robots_url}: {str(e)}")
                # Create an empty parser that allows all access if robots.txt can't be loaded
                rp = RobotFileParser()
                rp.allow_all = True

            self._robot_parsers[domain] = rp

        return self._robot_parsers[domain]

    def can_fetch(self, url: str, user_agent: str = '*') -> bool:
        """
        Check if the given URL can be fetched according to robots.txt.

        Args:
            url: URL to check
            user_agent: User agent to check for (default: '*')

        Returns:
            bool: True if URL can be fetched, False otherwise
        """
        if not self.respect_robots:
            return True

        rp = self._get_robot_parser(url)
        if hasattr(rp, 'allow_all') and rp.allow_all:
            return True

        try:
            return rp.can_fetch(user_agent, url)
        except Exception as e:
            logger.warning(f"Error checking robots.txt for {url}: {str(e)}")
            return True  # Default to allowing if there's an error

    def get_crawl_delay(self, user_agent: str = '*') -> float:
        """
        Get the crawl delay specified in robots.txt.

        Args:
            user_agent: User agent to check for (default: '*')

        Returns:
            float: Crawl delay in seconds, or default delay if not specified
        """
        if not self.respect_robots:
            return self.delay

        rp = self._get_robot_parser(self.base_url)
        if hasattr(rp, 'allow_all') and rp.allow_all:
            return self.delay

        try:
            robots_delay = rp.crawl_delay(user_agent)
            if robots_delay is not None:
                logger.info(f"Using crawl delay from robots.txt: {robots_delay}s")
                return max(robots_delay, self.delay)  # Use the larger of robots.txt delay or config delay
        except Exception as e:
            logger.warning(f"Error getting crawl delay from robots.txt: {str(e)}")

        return self.delay

    def enforce_delay(self) -> None:
        """
        Enforce the appropriate delay between requests.
        """
        if self.last_request_time is not None:
            # Calculate required delay
            delay = self.get_crawl_delay()

            # Add some randomization to be extra respectful
            delay += random.uniform(0.1, 0.5)

            elapsed = (datetime.now() - self.last_request_time).total_seconds()
            remaining_delay = delay - elapsed

            if remaining_delay > 0:
                logger.debug(f"Enforcing delay: sleeping for {remaining_delay:.2f}s")
                time.sleep(remaining_delay)

        self.last_request_time = datetime.now()

    @retry_crawl
    def fetch_page_with_respect(self, url: str, timeout: int = 30) -> requests.Response:
        """
        Fetch a page with respectful crawling practices.

        Args:
            url: URL to fetch
            timeout: Request timeout in seconds

        Returns:
            requests.Response: Response object

        Raises:
            CrawlError: If the page cannot be fetched
        """
        # Check robots.txt before fetching
        if not self.can_fetch(url):
            raise CrawlError(f"Robots.txt disallows fetching {url}")

        # Enforce delay between requests
        self.enforce_delay()

        logger.info(f"Fetching page: {url}")

        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()

            # Check if the response is HTML
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                raise CrawlError(f"URL does not return HTML content: {url}, content-type: {content_type}")

            logger.debug(f"Successfully fetched page {url}, status: {response.status_code}, content length: {len(response.text)}")
            return response
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to fetch page {url}: {str(e)}"
            logger.error(error_msg)
            raise CrawlError(error_msg) from e

    def crawl_multiple_pages(self, urls: List[str], timeout: int = 30) -> Dict[str, Optional[requests.Response]]:
        """
        Crawl multiple pages with respectful delays and robots.txt compliance.

        Args:
            urls: List of URLs to crawl
            timeout: Request timeout in seconds

        Returns:
            Dict[str, Optional[requests.Response]]: Dictionary mapping URLs to response objects (None if failed)
        """
        results = {}
        total_urls = len(urls)

        logger.info(f"Starting respectful crawl of {total_urls} pages")

        for i, url in enumerate(urls):
            try:
                logger.info(f"Crawling ({i+1}/{total_urls}): {url}")

                response = self.fetch_page_with_respect(url, timeout)
                results[url] = response

                logger.debug(f"Successfully crawled {url}")
            except CrawlError as e:
                logger.error(f"Crawl error for {url}: {str(e)}")
                results[url] = None
            except Exception as e:
                logger.error(f"Unexpected error crawling {url}: {str(e)}")
                results[url] = None

        logger.info(f"Respectful crawling completed for {total_urls} URLs")
        return results

    def get_sitemap_urls_with_respect(self, sitemap_url: str = None) -> List[str]:
        """
        Get URLs from sitemap with respectful crawling.

        Args:
            sitemap_url: URL of the sitemap (defaults to {base_url}/sitemap.xml)

        Returns:
            List[str]: List of URLs from the sitemap
        """
        if sitemap_url is None:
            sitemap_url = urljoin(self.base_url, 'sitemap.xml')

        # Fetch sitemap with respectful practices
        response = self.fetch_page_with_respect(sitemap_url)
        content = response.text

        # Parse sitemap (this would be done by the sitemap_parser module in practice)
        # For now, we'll just return an empty list - the actual parsing is in sitemap_parser.py
        from .sitemap_parser import SitemapParser
        parser = SitemapParser(self.base_url)
        urls = parser.parse_sitemap(content)

        return urls


def create_respectful_crawler(base_url: str = None, delay: float = None) -> RespectfulCrawler:
    """
    Create a respectful crawler instance with configuration.

    Args:
        base_url: Base URL of the website (defaults to config value)
        delay: Delay between requests in seconds (defaults to config value)

    Returns:
        RespectfulCrawler: Configured respectful crawler instance
    """
    return RespectfulCrawler(base_url, delay)


if __name__ == "__main__":
    # Test the respectful crawler
    print("Testing respectful crawler...")

    # Create a respectful crawler instance
    crawler = RespectfulCrawler()

    # Test robots.txt compliance
    test_url = config.book_base_url
    print(f"Testing robots.txt compliance for: {test_url}")
    can_fetch = crawler.can_fetch(test_url)
    print(f"Can fetch {test_url}: {can_fetch}")

    # Test crawl delay
    delay = crawler.get_crawl_delay()
    print(f"Effective crawl delay: {delay}s")

    # Test delay enforcement (uncomment to actually test the delay)
    print("Testing delay enforcement...")
    crawler.enforce_delay()
    print("Delay enforced successfully")

    print("Respectful crawler test completed")