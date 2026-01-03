"""
HTML content extraction and cleaning with error handling.
"""
import re
from bs4 import BeautifulSoup
from typing import Tuple, List
from urllib.parse import urlparse
from utils.logging_config import get_logger
from utils.error_handling import safe_execute
from models.data_models import Heading

logger = get_logger("content_extractor")


class ContentExtractor:
    """
    Extract content from HTML with comprehensive error handling and cleaning.
    """
    def __init__(self):
        self.default_title = "Untitled Page"

        # CSS selectors for elements to remove (navigation, footers, etc.)
        self.selectors_to_remove = [
            'nav', 'header', 'footer', 'aside',
            '.nav', '.navbar', '.navigation', '.menu',
            '.footer', '.sidebar', '.toc', '.table-of-contents',
            '.next-article', '.prev-article', '.article-nav',
            '.comments', '.comment', '.disqus', '.social',
            '.share', '.sharing', '.tags', '.categories',
            '.advertisement', '.ads', '.promo', '.banner',
            'script', 'style', 'noscript', 'iframe',
            '[role="navigation"]', '[role="banner"]', '[role="contentinfo"]'
        ]

        # Common class/id patterns for elements to remove
        self.patterns_to_remove = [
            r'.*nav.*', r'.*menu.*', r'.*header.*', r'.*footer.*',
            r'.*sidebar.*', r'.*toc.*', r'.*comments.*', r'.*social.*',
            r'.*share.*', r'.*tags.*', r'.*advertisement.*', r'.*ads.*'
        ]

    def extract_title(self, soup: BeautifulSoup, url: str) -> str:
        """
        Extract title from HTML soup with error handling.

        Args:
            soup: BeautifulSoup object
            url: URL of the page (for fallback)

        Returns:
            str: Extracted title or fallback
        """
        try:
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text().strip()
                if title:
                    return title

            # Try h1 as alternative title
            h1_tag = soup.find('h1')
            if h1_tag:
                h1_text = h1_tag.get_text().strip()
                if h1_text:
                    return h1_text

            # Fallback to URL path
            parsed_url = urlparse(url)
            path_parts = [part for part in parsed_url.path.split('/') if part]
            if path_parts:
                return path_parts[-1].replace('-', ' ').replace('_', ' ').title()

            return self.default_title
        except Exception as e:
            logger.error(f"Error extracting title from {url}: {str(e)}")
            # Fallback to URL path
            parsed_url = urlparse(url)
            path_parts = [part for part in parsed_url.path.split('/') if part]
            return path_parts[-1] if path_parts else self.default_title

    def extract_headings(self, soup: BeautifulSoup) -> List[Heading]:
        """
        Extract headings from HTML soup with hierarchy and error handling.

        Args:
            soup: BeautifulSoup object

        Returns:
            List[Heading]: List of Heading objects
        """
        headings = []
        try:
            heading_elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

            for i, heading_elem in enumerate(heading_elements):
                try:
                    level = int(heading_elem.name[1])  # Extract number from h1, h2, etc.
                    text = heading_elem.get_text().strip()

                    if text:  # Only add non-empty headings
                        # Create a simple path based on position and level
                        path_parts = []
                        for prev_heading in headings:
                            if prev_heading.level < level:
                                path_parts.append(prev_heading.text)

                        path_parts.append(text)
                        path = " > ".join(path_parts)

                        heading = Heading(
                            level=level,
                            text=text,
                            path=path,
                            position=heading_elem.sourceline or i
                        )
                        headings.append(heading)
                except Exception as e:
                    logger.warning(f"Error processing individual heading: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Error extracting headings: {str(e)}")

        return headings

    def clean_html(self, soup: BeautifulSoup) -> BeautifulSoup:
        """
        Clean HTML by removing unwanted elements like navigation, footers, etc.

        Args:
            soup: BeautifulSoup object to clean

        Returns:
            BeautifulSoup: Cleaned soup object
        """
        try:
            # Remove elements by CSS selectors
            for selector in self.selectors_to_remove:
                elements = soup.select(selector)
                for element in elements:
                    element.decompose()

            # Remove elements by class/id patterns
            for pattern in self.patterns_to_remove:
                # Find elements with class attributes matching the pattern
                elements = soup.find_all(attrs={"class": re.compile(pattern, re.IGNORECASE)})
                for element in elements:
                    element.decompose()

                # Find elements with id attributes matching the pattern
                elements = soup.find_all(attrs={"id": re.compile(pattern, re.IGNORECASE)})
                for element in elements:
                    element.decompose()

            # Remove elements that look like they contain only navigation links
            all_links = soup.find_all('a')
            for link in all_links:
                parent = link.parent
                if parent:
                    # If a parent element contains mostly links and little text, it might be navigation
                    link_count = len(parent.find_all('a'))
                    text_length = len(parent.get_text(strip=True))
                    if link_count > 5 and text_length / (link_count + 1) < 10:  # Heuristic
                        parent.decompose()

            return soup
        except Exception as e:
            logger.error(f"Error cleaning HTML: {str(e)}")
            # Return original soup if cleaning fails
            return soup

    def extract_text_content(self, soup: BeautifulSoup) -> str:
        """
        Extract clean text content from HTML soup with error handling.

        Args:
            soup: BeautifulSoup object

        Returns:
            str: Clean text content
        """
        try:
            # Clean the HTML first
            cleaned_soup = self.clean_html(soup)

            # Get text and clean it up
            text = cleaned_soup.get_text()

            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text_content = ' '.join(chunk for chunk in chunks if chunk)

            return text_content
        except Exception as e:
            logger.error(f"Error extracting text content: {str(e)}")
            return ""

    def extract_content(self, html_content: str, url: str) -> Tuple[str, str, List[Heading]]:
        """
        Extract title, text content, and headings from HTML with comprehensive error handling.

        Args:
            html_content: HTML content to extract from
            url: URL of the page

        Returns:
            Tuple[str, str, List[Heading]]: (title, text_content, headings)
        """
        try:
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')

            # Extract components
            title = safe_execute(
                lambda: self.extract_title(soup, url),
                fallback_value=self.default_title,
                logger_instance=logger
            )

            headings = safe_execute(
                lambda: self.extract_headings(soup),
                fallback_value=[],
                logger_instance=logger
            )

            text_content = safe_execute(
                lambda: self.extract_text_content(soup),
                fallback_value="",
                logger_instance=logger
            )

            logger.debug(f"Successfully extracted content from {url}: title='{title}', text_length={len(text_content)}, headings_count={len(headings)}")
            return title, text_content, headings

        except Exception as e:
            logger.error(f"Critical error extracting content from {url}: {str(e)}")
            # Return safe defaults
            return self.default_title, "", []


def extract_content_from_html(html_content: str, url: str) -> Tuple[str, str, List[Heading]]:
    """
    Convenience function to extract content from HTML.

    Args:
        html_content: HTML content to extract from
        url: URL of the page

    Returns:
        Tuple[str, str, List[Heading]]: (title, text_content, headings)
    """
    extractor = ContentExtractor()
    return extractor.extract_content(html_content, url)


def extract_title_from_html(html_content: str, url: str) -> str:
    """
    Convenience function to extract title from HTML.

    Args:
        html_content: HTML content to extract from
        url: URL of the page

    Returns:
        str: Extracted title
    """
    extractor = ContentExtractor()
    title, _, _ = extractor.extract_content(html_content, url)
    return title


def extract_text_from_html(html_content: str, url: str) -> str:
    """
    Convenience function to extract text content from HTML.

    Args:
        html_content: HTML content to extract from
        url: URL of the page

    Returns:
        str: Extracted text content
    """
    extractor = ContentExtractor()
    _, text_content, _ = extractor.extract_content(html_content, url)
    return text_content


def extract_headings_from_html(html_content: str, url: str) -> List[Heading]:
    """
    Convenience function to extract headings from HTML.

    Args:
        html_content: HTML content to extract from
        url: URL of the page

    Returns:
        List[Heading]: List of Heading objects
    """
    extractor = ContentExtractor()
    _, _, headings = extractor.extract_content(html_content, url)
    return headings


if __name__ == "__main__":
    # Test the content extractor
    print("Testing content extractor...")

    # Sample HTML content for testing
    sample_html = """
    <html>
    <head>
        <title>Sample Book Page</title>
    </head>
    <body>
        <h1>Chapter 1: Introduction</h1>
        <h2>Section A: Overview</h2>
        <p>This is the introduction to the first chapter.</p>
        <h3>Subsection 1.1: Key Concepts</h3>
        <p>Here are some key concepts...</p>
        <h2>Section B: Details</h2>
        <p>More details about the topic.</p>
    </body>
    </html>
    """

    url = "https://example.com/book/chapter1"

    title, text_content, headings = extract_content_from_html(sample_html, url)

    print(f"Extracted title: {title}")
    print(f"Text length: {len(text_content)} characters")
    print(f"Found {len(headings)} headings:")

    for i, heading in enumerate(headings):
        print(f"  {i+1}. Level {heading.level}: {heading.text} (path: {heading.path})")