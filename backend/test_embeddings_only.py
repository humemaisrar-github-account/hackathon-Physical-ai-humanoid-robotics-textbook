"""
Test script to verify text to embedding conversion functionality without Qdrant dependency.
"""
import sys
import os
from typing import List

# Add the backend/src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.text_embedding_service import create_text_embedding_service


def test_text_to_embedding_conversion():
    """
    Test the text to embedding conversion functionality without Qdrant.
    """
    print("Testing Text to Embedding Conversion (without Qdrant)")
    print("=" * 55)

    # Create the service
    service = create_text_embedding_service()

    # Test single text embedding
    print("\n1. Testing single text embedding:")
    test_text = "This is a test text for embedding"
    print(f"   Input: '{test_text}'")

    try:
        embedding = service.convert_single_text_to_embedding(test_text)
        print(f"   SUCCESS: Generated embedding with {len(embedding)} dimensions")
        print(f"   Sample: {embedding[:10]}...")  # Show first 10 values
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

    # Test multiple text embeddings
    print("\n2. Testing multiple text embeddings:")
    test_texts = [
        "First test text about artificial intelligence",
        "Second test text about machine learning",
        "Third test text about natural language processing"
    ]
    print(f"   Input: {len(test_texts)} texts")

    try:
        embeddings = service.convert_text_to_embeddings(test_texts)
        print(f"   SUCCESS: Generated {len(embeddings)} embeddings")
        print(f"   Each embedding has {len(embeddings[0])} dimensions")

        # Verify each embedding has the same dimensions
        for i, emb in enumerate(embeddings):
            if len(emb) != len(embeddings[0]):
                print(f"   ERROR: Embedding {i} has different dimensions")
                return False
        print("   SUCCESS: All embeddings have consistent dimensions")
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

    # Test edge cases
    print("\n3. Testing edge cases:")

    # Empty list
    try:
        empty_result = service.convert_text_to_embeddings([])
        print(f"   SUCCESS: Empty list handled, returned {len(empty_result)} embeddings")
    except Exception as e:
        print(f"   ERROR with empty list: {e}")
        return False

    # Single character
    try:
        single_char_emb = service.convert_single_text_to_embedding("A")
        print(f"   SUCCESS: Single character handled, embedding has {len(single_char_emb)} dimensions")
    except Exception as e:
        print(f"   ERROR with single character: {e}")
        return False

    print("\n" + "=" * 55)
    print("All text-to-embedding tests passed!")
    print("\nSummary of functionality:")
    print("- SUCCESS: Convert single text to embedding")
    print("- SUCCESS: Convert multiple texts to embeddings")
    print("- SUCCESS: Handle edge cases (empty lists, single characters)")
    print("- SUCCESS: Generate consistent embedding dimensions")
    print("- SUCCESS: Integration with Cohere API")

    return True


if __name__ == "__main__":
    print("Text Embedding Functionality Test")
    print("=" * 40)

    success = test_text_to_embedding_conversion()

    if success:
        print("\nSUCCESS: All tests passed! Text embedding functionality works correctly.")
        print("\nNote: This test verifies the text-to-embedding conversion functionality.")
        print("For full functionality including Qdrant storage and retrieval,")
        print("a working Qdrant instance would be required.")
    else:
        print("\nFAILED: Some tests failed!")
        sys.exit(1)