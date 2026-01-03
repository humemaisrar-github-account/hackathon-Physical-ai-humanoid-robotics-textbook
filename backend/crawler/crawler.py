"""
Main crawling module with requests/BeautifulSoup implementation.
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin, urlparse
from datetime import datetime
import time
import os
import json
from pathlib import Path

from utils.logging_config import get_logger, log_progress
from utils.error_handling import retry_crawl, CrawlError
from models.data_models import BookPage, BookPageStatus, Heading
from config.config import config

logger = get_logger("crawler")


class BookCrawler:
    """
    Main crawler class for crawling book pages and extracting content.
    """
    def __init__(self, base_url: str = None, delay: float = None):
        """
        Initialize the book crawler.

        Args:
            base_url: Base URL of the book (defaults to config value)
            delay: Delay between requests in seconds (defaults to config value)
        """
        self.base_url = base_url or config.book_base_url
        self.delay = delay or config.crawl_delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; BookCrawler/1.0; +http://example.com/bot)'
        })
        self.crawled_pages: Dict[str, BookPage] = {}
        self.failed_urls: List[str] = []

    @retry_crawl
    def fetch_page(self, url: str) -> str:
        """
        Fetch the content of a single page.

        Args:
            url: URL of the page to fetch

        Returns:
            str: HTML content of the page

        Raises:
            CrawlError: If the page cannot be fetched
        """
        logger.info(f"Fetching page: {url}")

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            # Check if the response is HTML
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                raise CrawlError(f"URL does not return HTML content: {url}, content-type: {content_type}")

            logger.debug(f"Successfully fetched page {url}, content length: {len(response.text)}")
            return response.text
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to fetch page {url}: {str(e)}"
            logger.error(error_msg)
            raise CrawlError(error_msg) from e

    def parse_page_content(self, html_content: str, url: str) -> tuple:
        """
        Parse HTML content and extract title, text, and headings.

        Args:
            html_content: HTML content to parse
            url: URL of the page (for context)

        Returns:
            tuple: (title, text_content, headings_list)
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract title
        title_tag = soup.find('title')
        title = title_tag.get_text().strip() if title_tag else urlparse(url).path.split('/')[-1] or 'Untitled'

        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()

        # Extract headings with hierarchy
        headings = []
        heading_elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

        for i, heading_elem in enumerate(heading_elements):
            level = int(heading_elem.name[1])  # Extract number from h1, h2, etc.
            text = heading_elem.get_text().strip()
            if text:  # Only add non-empty headings
                # Create a simple path based on position and level
                path_parts = [h.text for h in headings if h.level < level]
                path_parts.append(text)
                path = " > ".join(path_parts)

                heading = Heading(
                    level=level,
                    text=text,
                    path=path,
                    position=heading_elem.sourceline or i
                )
                headings.append(heading)

        # Extract main text content
        text_content = soup.get_text()

        # Clean up whitespace
        lines = (line.strip() for line in text_content.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text_content = ' '.join(chunk for chunk in chunks if chunk)

        logger.debug(f"Parsed page {url}: title='{title}', text_length={len(text_content)}, headings_count={len(headings)}")
        return title, text_content, headings

    def crawl_single_page(self, url: str) -> BookPage:
        """
        Crawl a single page and return a BookPage object.

        Args:
            url: URL of the page to crawl

        Returns:
            BookPage: BookPage object with crawled content
        """
        try:
            html_content = self.fetch_page(url)
            title, text_content, headings = self.parse_page_content(html_content, url)

            book_page = BookPage(
                url=url,
                title=title,
                content=html_content,
                text_content=text_content,
                headings=headings,
                created_at=datetime.now(),
                status=BookPageStatus.SUCCESS
            )

            logger.info(f"Successfully crawled page: {url}")
            return book_page

        except Exception as e:
            logger.error(f"Error crawling page {url}: {str(e)}")

            # Create a BookPage object with error status
            error_page = BookPage(
                url=url,
                title="",
                content="",
                text_content="",
                headings=[],
                created_at=datetime.now(),
                status=BookPageStatus.ERROR
            )
            self.failed_urls.append(url)
            return error_page

    def crawl_pages(self, urls: List[str]) -> List[BookPage]:
        """
        Crawl multiple pages from a list of URLs.

        Args:
            urls: List of URLs to crawl

        Returns:
            List[BookPage]: List of BookPage objects
        """
        if not urls:
            logger.warning("No URLs provided to crawl")
            return []

        book_pages = []
        total_urls = len(urls)

        logger.info(f"Starting to crawl {total_urls} pages")

        for i, url in enumerate(urls):
            try:
                # Respectful crawling - add delay between requests
                if i > 0:
                    time.sleep(self.delay)

                logger.info(f"Crawling ({i+1}/{total_urls}): {url}")

                book_page = self.crawl_single_page(url)
                book_pages.append(book_page)

                # Track the page
                self.crawled_pages[url] = book_page

                # Log progress
                log_progress(logger, i + 1, total_urls, "pages")

            except Exception as e:
                logger.error(f"Unexpected error crawling {url}: {str(e)}")
                self.failed_urls.append(url)

        success_count = len(book_pages) - len(self.failed_urls)
        logger.info(f"Crawling completed: {success_count} successful, {len(self.failed_urls)} failed out of {total_urls} total")

        return book_pages

    def save_crawled_pages(self, pages: List[BookPage], output_dir: str = None) -> bool:
        """
        Save crawled pages to files.

        Args:
            pages: List of BookPage objects to save
            output_dir: Directory to save pages (defaults to config value)

        Returns:
            bool: True if saving was successful
        """
        output_dir = output_dir or config.pages_dir
        os.makedirs(output_dir, exist_ok=True)

        saved_count = 0
        for page in pages:
            try:
                # Create a safe filename from the URL
                safe_filename = "".join(c for c in page.url if c.isalnum() or c in ('-', '_', '.'))[:100] + ".json"
                filepath = os.path.join(output_dir, safe_filename)

                # Save as JSON
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(page.json(indent=2))

                saved_count += 1
            except Exception as e:
                logger.error(f"Error saving page {page.url} to {filepath}: {str(e)}")

        logger.info(f"Saved {saved_count} pages to {output_dir}")
        return saved_count == len(pages)

    def check_robots_txt(self, base_url: str = None) -> bool:
        """
        Check robots.txt for crawling permissions (basic implementation).

        Args:
            base_url: Base URL to check robots.txt for (defaults to instance base_url)

        Returns:
            bool: True if crawling appears to be allowed
        """
        base_url = base_url or self.base_url
        robots_url = urljoin(base_url, 'robots.txt')

        try:
            response = self.session.get(robots_url, timeout=10)
            if response.status_code == 200:
                content = response.text.lower()
                # Simple check: if there's no explicit disallow for our user agent, assume it's ok
                if 'user-agent: *' in content and 'disallow: /' in content:
                    logger.warning(f"Robots.txt at {robots_url} may disallow crawling")
                    return False
            return True
        except Exception:
            # If robots.txt doesn't exist or can't be fetched, assume crawling is allowed
            logger.warning(f"Could not fetch robots.txt from {robots_url}, assuming crawling is allowed")
            return True


def crawl_book_pages(urls: List[str], base_url: str = None, delay: float = None) -> List[BookPage]:
    """
    Convenience function to crawl book pages.

    Args:
        urls: List of URLs to crawl
        base_url: Base URL of the book (defaults to config value)
        delay: Delay between requests in seconds (defaults to config value)

    Returns:
        List[BookPage]: List of BookPage objects
    """
    crawler = BookCrawler(base_url, delay)

    # Check robots.txt first
    if not crawler.check_robots_txt():
        logger.warning("Robots.txt check failed, proceeding with crawl anyway (respectful crawling enabled)")

    pages = crawler.crawl_pages(urls)
    crawler.save_crawled_pages(pages)

    return pages


def crawl_single_page(url: str, base_url: str = None) -> BookPage:
    """
    Convenience function to crawl a single page.

    Args:
        url: URL of the page to crawl
        base_url: Base URL of the book (defaults to config value)

    Returns:
        BookPage: BookPage object with crawled content
    """
    crawler = BookCrawler(base_url)
    page = crawler.crawl_single_page(url)
    crawler.save_crawled_pages([page])
    return page


if __name__ == "__main__":
    # Test the crawler
    print("Testing crawler module...")

    # Example usage with a few sample URLs
    # Note: In a real scenario, these would come from the sitemap parser
    sample_urls = [
        config.book_base_url,  # The main page
    ]

    # If we have more specific URLs, add them here
    # For now, let's just test with the base URL
    print(f"Crawling from base URL: {config.book_base_url}")

    try:
        # For testing purposes, we'll create a dummy URL list
        # In practice, this would come from sitemap_parser.discover_urls_from_sitemap()
        test_urls = [config.book_base_url]

        print(f"Attempting to crawl: {test_urls}")

        # Perform the crawl
        crawled_pages = crawl_book_pages(test_urls)

        print(f"\nCrawling completed!")
        print(f"Successfully crawled: {len(crawled_pages)} pages")
        print(f"Failed: {len([p for p in crawled_pages if p.status == BookPageStatus.ERROR])} pages")

        # Print details of first page if available
        if crawled_pages:
            first_page = crawled_pages[0]
            print(f"\nFirst page details:")
            print(f"  URL: {first_page.url}")
            print(f"  Title: {first_page.title}")
            print(f"  Status: {first_page.status}")
            print(f"  Text length: {len(first_page.text_content)} characters")
            print(f"  Headings: {len(first_page.headings)}")
            if first_page.headings:
                print(f"  First heading: {first_page.headings[0].text}")

    except Exception as e:
        print(f"Error during crawling: {e}")
        print("Make sure the BOOK_BASE_URL in your config is set correctly.")