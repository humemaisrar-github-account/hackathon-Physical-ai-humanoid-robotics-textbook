"""
Text chunking module with token-based segmentation.
"""
import uuid
from typing import List, Tuple, Optional
from datetime import datetime

from utils.logging_config import get_logger
from utils.token_utils import split_text_by_tokens_default, validate_chunk_size
from models.data_models import TextChunk, TextChunkStatus
from config.config import config

logger = get_logger("text_chunker")


class TextChunker:
    """
    Text chunking class for splitting content into token-based chunks with overlap.
    """
    def __init__(
        self,
        min_tokens: int = None,
        max_tokens: int = None,
        overlap_percent: float = None
    ):
        """
        Initialize the text chunker.

        Args:
            min_tokens: Minimum tokens per chunk (defaults to config)
            max_tokens: Maximum tokens per chunk (defaults to config)
            overlap_percent: Overlap percentage between chunks (defaults to config)
        """
        self.min_tokens = min_tokens or config.token_min
        self.max_tokens = max_tokens or config.token_max
        self.overlap_percent = overlap_percent or config.chunk_overlap_percent

        if self.min_tokens > self.max_tokens:
            raise ValueError(f"min_tokens ({self.min_tokens}) cannot be greater than max_tokens ({self.max_tokens})")

        if self.overlap_percent < 0 or self.overlap_percent > 50:
            raise ValueError(f"overlap_percent must be between 0 and 50, got {self.overlap_percent}")

    def chunk_text(
        self,
        text: str,
        page_url: str = "",
        heading_path: str = "",
        chunk_prefix: str = "chunk"
    ) -> List[TextChunk]:
        """
        Chunk text into segments based on token count with overlap.

        Args:
            text: The text to chunk
            page_url: URL of the source page
            heading_path: Hierarchical path of headings for context
            chunk_prefix: Prefix to use for chunk IDs

        Returns:
            List[TextChunk]: List of TextChunk objects
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for chunking")
            return []

        # Use the default token splitting function from utils
        chunks_with_tokens = split_text_by_tokens_default(text)

        text_chunks = []
        for i, (chunk_text, token_count) in enumerate(chunks_with_tokens):
            if not chunk_text.strip():
                continue  # Skip empty chunks

            # Validate chunk size
            is_valid = validate_chunk_size(
                token_count,
                min_tokens=self.min_tokens,
                max_tokens=self.max_tokens
            )

            if not is_valid:
                logger.warning(f"Chunk {i+1} has {token_count} tokens, outside range [{self.min_tokens}, {self.max_tokens}]")

                # For debugging: let's see if we can create smaller chunks that still meet TextChunk minimum
                # TextChunk model requires token_count >= 100, so if it's between 100 and our min, we can include it
                if 100 <= token_count <= self.max_tokens:
                    logger.info(f"Chunk {i+1} has {token_count} tokens, below minimum but above TextChunk requirement - including it")
                else:
                    # Skip creating TextChunk for invalid chunks to avoid validation errors
                    continue

            # Create chunk ID - use full UUID to ensure Qdrant compatibility
            chunk_id = str(uuid.uuid4())

            # Create TextChunk object
            text_chunk = TextChunk(
                chunk_id=chunk_id,
                page_url=page_url,
                heading_path=heading_path,
                content_raw=chunk_text,
                token_count=token_count,
                position_in_page=i,
                status=TextChunkStatus.PENDING
            )

            text_chunks.append(text_chunk)

        logger.info(f"Created {len(text_chunks)} chunks from text (original length: {len(text)} chars)")
        return text_chunks

    def chunk_multiple_texts(
        self,
        texts: List[Tuple[str, str, str]]  # List of (text, page_url, heading_path)
    ) -> List[TextChunk]:
        """
        Chunk multiple texts at once.

        Args:
            texts: List of tuples containing (text, page_url, heading_path)

        Returns:
            List[TextChunk]: List of all TextChunk objects
        """
        all_chunks = []
        total_texts = len(texts)

        for i, (text, page_url, heading_path) in enumerate(texts):
            logger.info(f"Chunking text {i+1}/{total_texts} from {page_url}")
            chunks = self.chunk_text(text, page_url, heading_path, f"chunk_{i+1:03d}")
            all_chunks.extend(chunks)

        logger.info(f"Total chunks created from {total_texts} texts: {len(all_chunks)}")
        return all_chunks


def chunk_text_content(
    text: str,
    page_url: str = "",
    heading_path: str = "",
    min_tokens: int = None,
    max_tokens: int = None,
    overlap_percent: float = None
) -> List[TextChunk]:
    """
    Convenience function to chunk text content.

    Args:
        text: The text to chunk
        page_url: URL of the source page
        heading_path: Hierarchical path of headings for context
        min_tokens: Minimum tokens per chunk (defaults to config)
        max_tokens: Maximum tokens per chunk (defaults to config)
        overlap_percent: Overlap percentage between chunks (defaults to config)

    Returns:
        List[TextChunk]: List of TextChunk objects
    """
    chunker = TextChunker(min_tokens, max_tokens, overlap_percent)
    return chunker.chunk_text(text, page_url, heading_path)


def chunk_multiple_text_contents(
    texts: List[Tuple[str, str, str]],
    min_tokens: int = None,
    max_tokens: int = None,
    overlap_percent: float = None
) -> List[TextChunk]:
    """
    Convenience function to chunk multiple text contents.

    Args:
        texts: List of tuples containing (text, page_url, heading_path)
        min_tokens: Minimum tokens per chunk (defaults to config)
        max_tokens: Maximum tokens per chunk (defaults to config)
        overlap_percent: Overlap percentage between chunks (defaults to config)

    Returns:
        List[TextChunk]: List of all TextChunk objects
    """
    chunker = TextChunker(min_tokens, max_tokens, overlap_percent)
    return chunker.chunk_multiple_texts(texts)


def validate_chunk(text_chunk: TextChunk) -> bool:
    """
    Validate a text chunk against size requirements.

    Args:
        text_chunk: TextChunk object to validate

    Returns:
        bool: True if chunk is valid, False otherwise
    """
    return validate_chunk_size(
        text_chunk.token_count,
        min_tokens=config.token_min,
        max_tokens=config.token_max
    )


def get_chunk_stats(chunks: List[TextChunk]) -> dict:
    """
    Get statistics about a list of chunks.

    Args:
        chunks: List of TextChunk objects

    Returns:
        dict: Statistics about the chunks
    """
    if not chunks:
        return {
            "total_chunks": 0,
            "avg_token_count": 0,
            "min_token_count": 0,
            "max_token_count": 0,
            "valid_chunks": 0,
            "invalid_chunks": 0
        }

    token_counts = [chunk.token_count for chunk in chunks]
    valid_chunks = [chunk for chunk in chunks if validate_chunk(chunk)]

    stats = {
        "total_chunks": len(chunks),
        "avg_token_count": sum(token_counts) / len(token_counts) if token_counts else 0,
        "min_token_count": min(token_counts) if token_counts else 0,
        "max_token_count": max(token_counts) if token_counts else 0,
        "valid_chunks": len(valid_chunks),
        "invalid_chunks": len(chunks) - len(valid_chunks)
    }

    return stats


if __name__ == "__main__":
    # Test the text chunker
    print("Testing text chunker...")

    # Sample text for testing
    sample_text = "This is a sample text. " * 100  # Create a longer text
    sample_text += "This section has different content for variety. " * 50

    print(f"Original text length: {len(sample_text)} characters")

    # Test chunking
    chunks = chunk_text_content(
        sample_text,
        page_url="https://example.com/sample-page",
        heading_path="Chapter 1 > Section A"
    )

    print(f"Number of chunks created: {len(chunks)}")

    # Print details of first few chunks
    for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
        print(f"Chunk {i+1}:")
        print(f"  ID: {chunk.chunk_id}")
        print(f"  Token count: {chunk.token_count}")
        print(f"  Content length: {len(chunk.content_raw)} characters")
        print(f"  Page URL: {chunk.page_url}")
        print(f"  Heading path: {chunk.heading_path}")
        print(f"  Position: {chunk.position_in_page}")
        print(f"  Status: {chunk.status}")
        print()

    # Get statistics
    stats = get_chunk_stats(chunks)
    print("Chunk statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Test validation
    if chunks:
        first_chunk_valid = validate_chunk(chunks[0])
        print(f"First chunk validation: {first_chunk_valid}")