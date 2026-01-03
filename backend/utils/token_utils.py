"""
Utility functions for token counting using tiktoken.
"""
import tiktoken
from typing import List, Tuple
from config.config import config


def get_tokenizer(encoding_name: str = "cl100k_base") -> tiktoken.Encoding:
    """
    Get a tokenizer for the specified encoding.

    Args:
        encoding_name: Name of the encoding to use (default: "cl100k_base" which is used by gpt-4, gpt-3.5-turbo, text-embedding-ada-002)

    Returns:
        tiktoken.Encoding: The tokenizer instance
    """
    return tiktoken.get_encoding(encoding_name)


def count_tokens(text: str, encoding_name: str = "cl100k_base") -> int:
    """
    Count the number of tokens in a text string.

    Args:
        text: The text to count tokens for
        encoding_name: Name of the encoding to use

    Returns:
        int: Number of tokens in the text
    """
    if not text:
        return 0

    tokenizer = get_tokenizer(encoding_name)
    tokens = tokenizer.encode(text)
    return len(tokens)


def split_text_by_tokens(
    text: str,
    max_tokens: int = 500,
    min_tokens: int = 2,
    overlap_percent: float = 15.0,
    encoding_name: str = "cl100k_base"
) -> List[Tuple[str, int]]:
    """
    Split text into chunks based on token count with overlap.

    Args:
        text: The text to split
        max_tokens: Maximum tokens per chunk (default: 500)
        min_tokens: Minimum tokens per chunk (default: 300)
        overlap_percent: Percentage of overlap between chunks (default: 15.0)
        encoding_name: Name of the encoding to use

    Returns:
        List[Tuple[str, int]]: List of tuples containing (chunk_text, token_count)
    """
    if not text:
        return []

    if max_tokens <= 0 or min_tokens <= 0 or min_tokens > max_tokens:
        raise ValueError("Invalid token range specified")

    if overlap_percent < 0 or overlap_percent > 50:
        raise ValueError("Overlap percentage must be between 0 and 50")

    tokenizer = get_tokenizer(encoding_name)
    tokens = tokenizer.encode(text)

    if len(tokens) <= max_tokens:
        return [(text, len(tokens))]

    chunks = []
    overlap_tokens = int(max_tokens * (overlap_percent / 100))

    start_idx = 0
    while start_idx < len(tokens):
        # Determine the end index for this chunk
        end_idx = start_idx + max_tokens

        # If this would exceed the text length, adjust it
        if end_idx > len(tokens):
            end_idx = len(tokens)

        # If the remaining text is less than min_tokens, add it to the last chunk
        if end_idx - start_idx < min_tokens and start_idx > 0:
            # Add the remaining tokens to the previous chunk
            prev_chunk_tokens, prev_chunk_start, prev_chunk_end = chunks[-1][2], chunks[-1][3], chunks[-1][4]
            chunks[-1] = (
                tokenizer.decode(tokens[prev_chunk_start:end_idx]),
                prev_chunk_end - prev_chunk_start,
                prev_chunk_start,
                prev_chunk_end,
                end_idx
            )
            break

        # Decode the current chunk
        chunk_text = tokenizer.decode(tokens[start_idx:end_idx])
        chunk_token_count = end_idx - start_idx

        # Store chunk text, token count, and indices for overlap calculation
        chunks.append((chunk_text, chunk_token_count, start_idx, end_idx, end_idx))

        # Move start index forward, accounting for overlap
        if end_idx < len(tokens):  # If not at the end
            start_idx = end_idx - overlap_tokens
        else:
            break

    # Extract just the text and token count for return
    result = [(chunk[0], chunk[1]) for chunk in chunks]
    return result


def validate_chunk_size(token_count: int, min_tokens: int = 300, max_tokens: int = 500) -> bool:
    """
    Validate if a token count is within the acceptable range.

    Args:
        token_count: Number of tokens to validate
        min_tokens: Minimum acceptable tokens (default: 300)
        max_tokens: Maximum acceptable tokens (default: 500)

    Returns:
        bool: True if token count is within range, False otherwise
    """
    return min_tokens <= token_count <= max_tokens


def get_approximate_word_count(text: str) -> int:
    """
    Get an approximate word count from text (for reference purposes).
    Note: This is not the same as token count, but can be useful for estimation.

    Args:
        text: The text to count words for

    Returns:
        int: Approximate word count
    """
    if not text:
        return 0
    # Simple word splitting (doesn't account for all edge cases)
    return len(text.split())


def get_tokens_per_word_approx(text: str) -> float:
    """
    Get an approximate ratio of tokens per word in the text.

    Args:
        text: The text to analyze

    Returns:
        float: Approximate tokens per word ratio
    """
    if not text:
        return 0.0

    word_count = get_approximate_word_count(text)
    token_count = count_tokens(text)

    if word_count == 0:
        return 0.0

    return token_count / word_count


def truncate_text_to_tokens(text: str, max_tokens: int, encoding_name: str = "cl100k_base") -> str:
    """
    Truncate text to a maximum number of tokens.

    Args:
        text: The text to truncate
        max_tokens: Maximum number of tokens allowed
        encoding_name: Name of the encoding to use

    Returns:
        str: Truncated text
    """
    if not text or max_tokens <= 0:
        return ""

    tokenizer = get_tokenizer(encoding_name)
    tokens = tokenizer.encode(text)

    if len(tokens) <= max_tokens:
        return text

    truncated_tokens = tokens[:max_tokens]
    return tokenizer.decode(truncated_tokens)


# Default tokenizer for the application
default_tokenizer = get_tokenizer()


def count_tokens_default(text: str) -> int:
    """
    Count tokens using the default tokenizer (convenience function).

    Args:
        text: The text to count tokens for

    Returns:
        int: Number of tokens in the text
    """
    return count_tokens(text, config.cohere_model.split('-')[-1] if 'multilingual' in config.cohere_model else "cl100k_base")


def split_text_by_tokens_default(text: str) -> List[Tuple[str, int]]:
    """
    Split text using more permissive configuration to generate more chunks.

    Args:
        text: The text to split

    Returns:
        List[Tuple[str, int]]: List of tuples containing (chunk_text, token_count)
    """
    # Use more permissive settings to generate more potential chunks
    # This will allow more content to be chunked even if it doesn't meet strict requirements
    return split_text_by_tokens(
        text,
        max_tokens=config.token_max,
        min_tokens=1,  # More permissive minimum for initial splitting
        overlap_percent=config.chunk_overlap_percent
    )


if __name__ == "__main__":
    # Test the token utilities
    test_text = "This is a test sentence. " * 100  # Create a longer text

    print(f"Test text length: {len(test_text)} characters")
    print(f"Token count: {count_tokens(test_text)}")
    print(f"Approximate word count: {get_approximate_word_count(test_text)}")
    print(f"Tokens per word ratio: {get_tokens_per_word_approx(test_text):.2f}")

    # Test chunking
    chunks = split_text_by_tokens(test_text, max_tokens=100, min_tokens=50, overlap_percent=20)
    print(f"\nNumber of chunks created: {len(chunks)}")

    for i, (chunk_text, token_count) in enumerate(chunks[:3]):  # Show first 3 chunks
        print(f"Chunk {i+1}: {token_count} tokens, {len(chunk_text)} characters")

    # Test validation
    print(f"\nValidation for 400 tokens: {validate_chunk_size(400)}")
    print(f"Validation for 600 tokens: {validate_chunk_size(600)}")