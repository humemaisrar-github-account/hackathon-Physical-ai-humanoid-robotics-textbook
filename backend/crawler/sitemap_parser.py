"""
Sitemap parser to discover all book page URLs.
"""
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse
from typing import List, Set
from utils.logging_config import get_logger
from utils.error_handling import retry_crawl, CrawlError
from config.config import config

logger = get_logger("sitemap_parser")


class SitemapParser:
    """
    Parser for sitemap.xml files to discover URLs.
    """
    def __init__(self, base_url: str = None):
        """
        Initialize the sitemap parser.

        Args:
            base_url: Base URL of the website (defaults to config value)
        """
        self.base_url = base_url or config.book_base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; BookCrawler/1.0; +http://example.com/bot)'
        })

    @retry_crawl
    def fetch_sitemap(self, sitemap_url: str = None) -> str:
        """
        Fetch the sitemap content from the given URL.

        Args:
            sitemap_url: URL of the sitemap (defaults to {base_url}/sitemap.xml)

        Returns:
            str: Content of the sitemap

        Raises:
            CrawlError: If the sitemap cannot be fetched
        """
        if sitemap_url is None:
            sitemap_url = urljoin(self.base_url, 'sitemap.xml')

        logger.info(f"Fetching sitemap from: {sitemap_url}")

        try:
            response = self.session.get(sitemap_url, timeout=30)
            response.raise_for_status()

            logger.info(f"Sitemap fetched successfully, content length: {len(response.text)}")
            return response.text
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to fetch sitemap from {sitemap_url}: {str(e)}"
            logger.error(error_msg)
            raise CrawlError(error_msg) from e

    def parse_sitemap(self, sitemap_content: str) -> List[str]:
        """
        Parse the sitemap XML content and extract URLs.

        Args:
            sitemap_content: XML content of the sitemap

        Returns:
            List[str]: List of URLs found in the sitemap
        """
        urls = []
        try:
            root = ET.fromstring(sitemap_content)

            # Handle both regular sitemap and sitemap index
            if root.tag.endswith('sitemapindex'):
                # This is a sitemap index, need to fetch individual sitemaps
                sitemap_locs = []
                for sitemap_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap/{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                    sitemap_locs.append(sitemap_elem.text.strip())

                for sitemap_loc in sitemap_locs:
                    logger.info(f"Processing nested sitemap: {sitemap_loc}")
                    nested_sitemap_content = self.fetch_sitemap(sitemap_loc)
                    nested_urls = self.parse_sitemap(nested_sitemap_content)
                    urls.extend(nested_urls)
            else:
                # This is a regular sitemap with URLs
                for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                    url = url_elem.text.strip()
                    urls.append(url)

        except ET.ParseError as e:
            error_msg = f"Failed to parse sitemap XML: {str(e)}"
            logger.error(error_msg)
            raise CrawlError(error_msg) from e

        logger.info(f"Found {len(urls)} URLs in sitemap")
        return urls

    def filter_urls(self, urls: List[str], include_patterns: List[str] = None, exclude_patterns: List[str] = None) -> List[str]:
        """
        Filter URLs based on include/exclude patterns.

        Args:
            urls: List of URLs to filter
            include_patterns: List of patterns that URLs must match (if provided)
            exclude_patterns: List of patterns that URLs must not match

        Returns:
            List[str]: Filtered list of URLs
        """
        filtered_urls = []

        for url in urls:
            # Check if URL is under the base domain
            parsed_url = urlparse(url)
            base_domain = urlparse(self.base_url).netloc

            if parsed_url.netloc != base_domain:
                continue  # Skip external links

            # Check include patterns
            if include_patterns:
                should_include = any(pattern in url for pattern in include_patterns)
                if not should_include:
                    continue

            # Check exclude patterns
            if exclude_patterns:
                should_exclude = any(pattern in url for pattern in exclude_patterns)
                if should_exclude:
                    continue

            filtered_urls.append(url)

        logger.info(f"Filtered URLs from {len(urls)} to {len(filtered_urls)}")
        return filtered_urls

    def get_all_urls(self, include_patterns: List[str] = None, exclude_patterns: List[str] = None) -> List[str]:
        """
        Get all URLs from the sitemap with optional filtering.

        Args:
            include_patterns: List of patterns that URLs must match
            exclude_patterns: List of patterns that URLs must not match

        Returns:
            List[str]: List of filtered URLs from the sitemap
        """
        sitemap_content = self.fetch_sitemap()
        urls = self.parse_sitemap(sitemap_content)
        filtered_urls = self.filter_urls(urls, include_patterns, exclude_patterns)

        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url in filtered_urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)

        logger.info(f"Total unique URLs after deduplication: {len(unique_urls)}")
        return unique_urls


def discover_urls_from_sitemap(base_url: str = None, include_patterns: List[str] = None, exclude_patterns: List[str] = None) -> List[str]:
    """
    Convenience function to discover all URLs from sitemap.

    Args:
        base_url: Base URL of the website (defaults to config value)
        include_patterns: List of patterns that URLs must match
        exclude_patterns: List of patterns that URLs must not match

    Returns:
        List[str]: List of URLs discovered from sitemap
    """
    parser = SitemapParser(base_url)
    return parser.get_all_urls(include_patterns, exclude_patterns)


def get_sitemap_urls_count(base_url: str = None) -> int:
    """
    Get the count of URLs in the sitemap.

    Args:
        base_url: Base URL of the website (defaults to config value)

    Returns:
        int: Number of URLs in the sitemap
    """
    urls = discover_urls_from_sitemap(base_url)
    return len(urls)


if __name__ == "__main__":
    # Test the sitemap parser
    print("Testing sitemap parser...")

    try:
        # Test fetching URLs from sitemap
        urls = discover_urls_from_sitemap()
        print(f"Found {len(urls)} URLs in sitemap")

        if urls:
            print("First 5 URLs:")
            for i, url in enumerate(urls[:5]):
                print(f"  {i+1}. {url}")

            if len(urls) > 5:
                print(f"  ... and {len(urls) - 5} more")

        # Test with filtering
        doc_urls = discover_urls_from_sitemap(include_patterns=['docs', 'tutorial'], exclude_patterns=['tag', 'category'])
        print(f"\nFound {len(doc_urls)} documentation URLs after filtering")

    except Exception as e:
        print(f"Error during sitemap parsing: {e}")
        print("This may be expected if the sitemap is not available at the default location.")
        print(f"Make sure the BOOK_BASE_URL in your config is set correctly: {config.book_base_url}")