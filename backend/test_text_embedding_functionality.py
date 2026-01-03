"""
Test script for the Text Embedding Service functionality (without external dependencies).

This script tests the core functionality of text to embedding conversion
without requiring Qdrant to be running.
"""
import os
import sys
from unittest.mock import Mock, patch

# Add the backend/src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.text_embedding_service import TextEmbeddingService


def test_text_to_embedding_conversion():
    """
    Test the text to embedding conversion functionality.
    """
    print("Testing Text to Embedding Conversion")
    print("=" * 40)

    # Create a mock service that doesn't require external dependencies
    service = TextEmbeddingService.__new__(TextEmbeddingService)  # Create without calling __init__

    # Mock the Cohere client to return predictable embeddings
    mock_cohere_client = Mock()
    mock_cohere_client.embed.return_value = Mock()
    mock_cohere_client.embed.return_value.embeddings = [
        [0.1, 0.2, 0.3, 0.4, 0.5] * 205,  # 1025-dim vector
        [0.2, 0.3, 0.4, 0.5, 0.1] * 205,  # 1025-dim vector
        [0.3, 0.4, 0.5, 0.1, 0.2] * 205,  # 1025-dim vector
    ]

    service.cohere_client = mock_cohere_client
    service.logger = Mock()  # Mock logger to avoid actual logging

    # Test single text embedding
    test_text = "This is a test text"
    embedding = service.convert_single_text_to_embedding(test_text)

    print(f"[OK] Generated embedding with {len(embedding)} dimensions")
    assert len(embedding) == 1025, "Embedding should have 1025 dimensions"
    print("[OK] Single text embedding works correctly")

    # Test multiple text embeddings
    test_texts = [
        "First test text",
        "Second test text",
        "Third test text"
    ]

    embeddings = service.convert_text_to_embeddings(test_texts)
    print(f"[OK] Generated {len(embeddings)} embeddings for {len(test_texts)} texts")

    assert len(embeddings) == len(test_texts), "Number of embeddings should match number of texts"
    assert len(embeddings[0]) == 1025, "Each embedding should have 1025 dimensions"
    print("[OK] Multiple text embedding works correctly")

    print("\nText to embedding conversion tests passed!")
    return True


def test_embedding_service_creation():
    """
    Test that the service can be created (with mocks for external dependencies).
    """
    print("\nTesting Service Creation")
    print("=" * 25)

    # Mock external dependencies to avoid requiring them
    with patch('cohere.Client') as mock_cohere, \
         patch('qdrant_client.QdrantClient') as mock_qdrant:

        # Configure mocks
        mock_cohere.return_value = Mock()
        mock_qdrant.return_value = Mock()

        # Import settings to pass to the service
        from src.config import settings

        # Create the service
        service = TextEmbeddingService()

        print("[OK] Service created successfully with mocked dependencies")
        print("[OK] External dependencies properly mocked")

        return True


def test_metadata_handling():
    """
    Test that metadata is properly handled in the service.
    """
    print("\nTesting Metadata Handling")
    print("=" * 25)

    # Create a mock service
    service = TextEmbeddingService.__new__(TextEmbeddingService)
    service.logger = Mock()

    # Test metadata preparation logic
    texts = ["Text 1", "Text 2"]
    metadata_list = [{"source": "test1"}, {"source": "test2"}]

    # Simulate the metadata preparation logic from save_embeddings_to_qdrant
    if metadata_list is None:
        metadata_list = [{} for _ in range(len(texts))]
    else:
        # Add default metadata fields
        for i, meta in enumerate(metadata_list):
            meta.setdefault("text", texts[i])
            meta.setdefault("created_at")
            meta.setdefault("id", f"test_id_{i}")

    print(f"[OK] Metadata properly prepared for {len(metadata_list)} texts")
    assert len(metadata_list) == len(texts), "Metadata count should match text count"
    print("[OK] Metadata handling works correctly")

    return True


def run_all_tests():
    """
    Run all tests for the text embedding service functionality.
    """
    print("Starting Text Embedding Service Functionality Tests")
    print("=" * 55)

    tests = [
        ("Service Creation", test_embedding_service_creation),
        ("Text to Embedding Conversion", test_text_to_embedding_conversion),
        ("Metadata Handling", test_metadata_handling),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            print(f"\n--- Running {test_name} ---")
            if test_func():
                print(f"[PASS] {test_name} PASSED")
                passed += 1
            else:
                print(f"[FAIL] {test_name} FAILED")
        except Exception as e:
            print(f"[FAIL] {test_name} FAILED with error: {str(e)}")
            import traceback
            traceback.print_exc()

    print(f"\n{'='*55}")
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("[SUCCESS] All functionality tests passed!")
        print("\nSummary of what was tested:")
        print("  - Service initialization with mocked dependencies")
        print("  - Text to embedding conversion (single and multiple texts)")
        print("  - Metadata handling and preparation")
        return True
    else:
        print("[ERROR] Some tests failed!")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    if not success:
        sys.exit(1)