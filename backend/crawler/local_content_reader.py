"""
Module to read and process local Docusaurus content instead of crawling from URLs.
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from utils.logging_config import get_logger
from models.data_models import BookPage, Heading, BookPageStatus
from config.config import config


logger = get_logger("local_content_reader")


class LocalDocusaurusReader:
    """
    Reader for local Docusaurus content files.
    """
    def __init__(self, docs_dir: str = None):
        """
        Initialize the local Docusaurus reader.

        Args:
            docs_dir: Path to the Docusaurus docs directory (defaults to config value)
        """
        self.docs_dir = docs_dir or config.local_docs_dir or "frontend/docs"
        if not os.path.exists(self.docs_dir):
            # Try alternative locations
            possible_paths = [
                "frontend/docs",
                "docs",
                "frontend/src/docs",
                "src/docs"
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    self.docs_dir = path
                    logger.info(f"Using docs directory: {self.docs_dir}")
                    break
            else:
                raise FileNotFoundError(f"Docs directory not found: {self.docs_dir}")

        logger.info(f"Initialized LocalDocusaurusReader with docs directory: {self.docs_dir}")

    def read_markdown_files(self) -> List[Dict[str, Any]]:
        """
        Read all markdown files from the docs directory.

        Returns:
            List of dictionaries containing file path, content, and metadata
        """
        markdown_files = []
        for root, dirs, files in os.walk(self.docs_dir):
            for file in files:
                if file.endswith(('.md', '.mdx')):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()

                        # Extract metadata from the file (frontmatter)
                        metadata = self._extract_frontmatter(content)

                        markdown_files.append({
                            'filepath': filepath,
                            'filename': file,
                            'relative_path': os.path.relpath(filepath, self.docs_dir),
                            'content': content,
                            'metadata': metadata
                        })

                        logger.debug(f"Read markdown file: {filepath}")
                    except Exception as e:
                        logger.error(f"Error reading file {filepath}: {e}")

        logger.info(f"Found {len(markdown_files)} markdown files in {self.docs_dir}")
        return markdown_files

    def _extract_frontmatter(self, content: str) -> Dict[str, Any]:
        """
        Extract frontmatter from markdown content.

        Args:
            content: Raw markdown content

        Returns:
            Dictionary containing frontmatter metadata
        """
        # Look for YAML frontmatter between --- delimiters
        frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if frontmatter_match:
            frontmatter_text = frontmatter_match.group(1)
            # Simple YAML-like parsing (not full YAML for simplicity)
            metadata = {}
            for line in frontmatter_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')  # Remove quotes
                    metadata[key] = value
            return metadata
        return {}

    def extract_headings(self, content: str, file_path: str = "") -> List[Heading]:
        """
        Extract headings from markdown content.

        Args:
            content: Markdown content
            file_path: Path of the file for context

        Returns:
            List of Heading objects
        """
        headings = []

        # Remove frontmatter if present for heading extraction
        content_without_frontmatter = re.sub(r'^---\s*\n(.*?)\n---\s*\n', '', content, flags=re.DOTALL)

        # Extract markdown headings (# ## ### etc.)
        heading_pattern = r'^(#{1,6})\s+(.+)$'
        lines = content_without_frontmatter.split('\n')

        for i, line in enumerate(lines):
            match = re.match(heading_pattern, line.strip())
            if match:
                level = len(match.group(1))  # Number of # symbols
                text = match.group(2).strip()

                # Create a simple path based on the file and heading hierarchy
                path = f"{os.path.basename(file_path)} > {text}" if file_path else text

                heading = Heading(
                    level=level,
                    text=text,
                    path=path,
                    position=i
                )
                headings.append(heading)

        logger.debug(f"Extracted {len(headings)} headings from {file_path}")
        return headings

    def extract_text_content(self, content: str) -> str:
        """
        Extract clean text content from markdown, removing markdown syntax.

        Args:
            content: Raw markdown content

        Returns:
            Clean text content
        """
        # Remove frontmatter
        content = re.sub(r'^---\s*\n(.*?)\n---\s*\n', '', content, flags=re.DOTALL)

        # Remove markdown formatting but keep the text
        # Remove headers but keep the text
        content = re.sub(r'^#{1,6}\s+', '', content, flags=re.MULTILINE)
        # Remove bold and italic formatting
        content = re.sub(r'\*{1,2}(.*?)\*{1,2}', r'\1', content)
        content = re.sub(r'_{1,2}(.*?)_{1,2}', r'\1', content)
        # Remove links [text](url) -> text
        content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)
        # Remove images
        content = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', content)
        # Remove code blocks
        content = re.sub(r'```.*?\n.*?```', '', content, flags=re.DOTALL)
        # Remove inline code
        content = re.sub(r'`(.*?)`', r'\1', content)

        # Clean up extra whitespace
        lines = (line.strip() for line in content.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text_content = ' '.join(chunk for chunk in chunks if chunk)

        return text_content

    def convert_to_book_pages(self, markdown_files: List[Dict[str, Any]]) -> List[BookPage]:
        """
        Convert markdown files to BookPage objects.

        Args:
            markdown_files: List of markdown file dictionaries

        Returns:
            List of BookPage objects
        """
        book_pages = []

        for file_data in markdown_files:
            try:
                # Extract title from filename or frontmatter
                title = file_data['metadata'].get('title', '')
                if not title:
                    title = os.path.splitext(file_data['filename'])[0].replace('-', ' ').replace('_', ' ').title()

                # Extract headings
                headings = self.extract_headings(file_data['content'], file_data['filepath'])

                # Extract clean text content
                text_content = self.extract_text_content(file_data['content'])

                # Create a URL-like identifier based on the file path
                relative_path = file_data['relative_path']
                # Convert file path to URL format (replace .md with no extension)
                url_path = relative_path.replace('\\', '/').replace('.md', '').replace('.mdx', '')
                if url_path.endswith('/index'):
                    url_path = url_path[:-6]  # Remove '/index'
                elif url_path == 'index':
                    url_path = ''

                # Create a proper URL format that satisfies the validation
                # Using a placeholder domain for local content
                url = f"https://local-content/{url_path.lstrip('/')}".replace('\\', '/')

                book_page = BookPage(
                    url=url,
                    title=title,
                    content=file_data['content'],  # Store raw content
                    text_content=text_content,
                    headings=headings,
                    created_at=datetime.now(),
                    status=BookPageStatus.SUCCESS
                )

                book_pages.append(book_page)
                logger.debug(f"Created BookPage for: {file_data['filepath']}")

            except Exception as e:
                logger.error(f"Error converting file {file_data['filepath']} to BookPage: {e}")
                # Create an error BookPage
                error_page = BookPage(
                    url=f"file:///{file_data['filepath']}",
                    title=os.path.basename(file_data['filepath']),
                    content="",
                    text_content="",
                    headings=[],
                    created_at=datetime.now(),
                    status=BookPageStatus.ERROR
                )
                book_pages.append(error_page)

        logger.info(f"Converted {len(markdown_files)} markdown files to {len(book_pages)} BookPage objects")
        return book_pages

    def read_docusaurus_content(self) -> List[BookPage]:
        """
        Read all Docusaurus content and convert to BookPage objects.

        Returns:
            List of BookPage objects representing all content
        """
        logger.info(f"Reading Docusaurus content from: {self.docs_dir}")

        # Read all markdown files
        markdown_files = self.read_markdown_files()

        if not markdown_files:
            logger.warning(f"No markdown files found in {self.docs_dir}")
            return []

        # Convert to BookPage objects
        book_pages = self.convert_to_book_pages(markdown_files)

        logger.info(f"Successfully read {len(book_pages)} pages from Docusaurus content")
        return book_pages


def read_local_docusaurus_content(docs_dir: str = None) -> List[BookPage]:
    """
    Convenience function to read local Docusaurus content.

    Args:
        docs_dir: Path to the Docusaurus docs directory (defaults to config value)

    Returns:
        List of BookPage objects
    """
    reader = LocalDocusaurusReader(docs_dir)
    return reader.read_docusaurus_content()


if __name__ == "__main__":
    # Test the local content reader
    print("Testing LocalDocusaurusReader...")

    try:
        # Try to read content from the default location
        pages = read_local_docusaurus_content()

        print(f"Successfully read {len(pages)} pages")

        if pages:
            # Print details of first few pages
            for i, page in enumerate(pages[:3]):
                print(f"\nPage {i+1}:")
                print(f"  URL: {page.url}")
                print(f"  Title: {page.title}")
                print(f"  Text length: {len(page.text_content)}")
                print(f"  Headings: {len(page.headings)}")
                if page.headings:
                    print(f"  First heading: {page.headings[0].text}")

        if len(pages) > 3:
            print(f"\n... and {len(pages) - 3} more pages")

    except Exception as e:
        print(f"Error reading local Docusaurus content: {e}")
        print("Make sure the docs directory exists and contains markdown files.")