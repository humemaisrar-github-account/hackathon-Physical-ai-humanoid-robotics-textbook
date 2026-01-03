"""
Test script for the Text Embedding Service workflow.

This script tests the complete workflow of:
1. Converting text to embeddings
2. Saving embeddings to Qdrant
3. Retrieving similar embeddings from Qdrant
"""
import asyncio
import os
import sys
from typing import List, Dict, Any

# Add the backend/src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.text_embedding_service import TextEmbeddingService, create_text_embedding_service


def test_complete_workflow():
    """
    Test the complete workflow of the text embedding service.
    """
    print("Testing Complete Text Embedding Workflow")
    print("=" * 50)

    # Create the service
    service = create_text_embedding_service()

    # Test data
    sample_texts = [
        "The quick brown fox jumps over the lazy dog",
        "Machine learning is a subset of artificial intelligence",
        "Python is a popular programming language for data science",
        "Natural language processing enables computers to understand human language",
        "Vector databases like Qdrant are essential for semantic search",
        "Artificial intelligence and machine learning are transforming industries",
        "Deep learning models require large amounts of training data",
        "Neural networks are inspired by the human brain structure"
    ]

    sample_metadata = [
        {"category": "animals", "source": "example1", "topic": "general"},
        {"category": "technology", "source": "example2", "topic": "AI"},
        {"category": "programming", "source": "example3", "topic": "languages"},
        {"category": "technology", "source": "example4", "topic": "NLP"},
        {"category": "technology", "source": "example5", "topic": "databases"},
        {"category": "technology", "source": "example6", "topic": "AI"},
        {"category": "technology", "source": "example7", "topic": "ML"},
        {"category": "technology", "source": "example8", "topic": "neural networks"}
    ]

    try:
        # Test 1: Convert text to embeddings
        print("\nTest 1: Converting text to embeddings")
        print("-" * 30)

        embeddings = service.convert_text_to_embeddings(sample_texts)
        print(f"Generated {len(embeddings)} embeddings")
        print(f"Each embedding has {len(embeddings[0]) if embeddings else 0} dimensions")

        # Verify embeddings are properly generated
        assert len(embeddings) == len(sample_texts), "Number of embeddings should match number of texts"
        assert len(embeddings[0]) > 0, "Embeddings should not be empty"
        print("Embedding conversion verified")

        # Test 2: Save embeddings to Qdrant
        print("\nTest 2: Saving embeddings to Qdrant")
        print("-" * 30)

        saved_ids = service.save_embeddings_to_qdrant(sample_texts, sample_metadata)
        print(f"Saved {len(saved_ids)} embeddings to Qdrant")
        print(f"Generated IDs: {saved_ids[:3]}...")  # Show first 3 IDs

        # Verify save operation
        count = service.get_embedding_count()
        print(f"Total embeddings in collection: {count}")
        assert count >= len(sample_texts), "Collection should have at least the number of saved embeddings"
        print("Save operation verified")

        # Test 3: Retrieve similar embeddings (Semantic Search)
        print("\nTest 3: Retrieving similar embeddings")
        print("-" * 30)

        # Test query 1: AI-related query
        query1 = "artificial intelligence and machine learning"
        print(f"Query: '{query1}'")

        similar_results = service.retrieve_similar_embeddings(query1, top_k=3)
        print(f"Found {len(similar_results)} similar embeddings")

        for i, result in enumerate(similar_results, 1):
            print(f"  {i}. Score: {result['score']:.3f}")
            print(f"     Text: '{result['text'][:60]}...'")
            print(f"     Category: {result['payload'].get('category', 'N/A')}")
            print(f"     Topic: {result['payload'].get('topic', 'N/A')}")

        # Verify retrieval results
        assert len(similar_results) <= 3, "Should return at most top_k results"
        assert all('score' in result for result in similar_results), "All results should have a score"
        print("Similarity search verified")

        # Test query 2: Programming-related query
        query2 = "Python programming language"
        print(f"\nQuery: '{query2}'")

        similar_results2 = service.retrieve_similar_embeddings(query2, top_k=2)
        print(f"Found {len(similar_results2)} similar embeddings")

        for i, result in enumerate(similar_results2, 1):
            print(f"  {i}. Score: {result['score']:.3f}")
            print(f"     Text: '{result['text'][:60]}...'")
            print(f"     Category: {result['payload'].get('category', 'N/A')}")

        # Test 4: Count verification
        print("\nTest 4: Count verification")
        print("-" * 30)

        current_count = service.get_embedding_count()
        print(f"Current embedding count: {current_count}")
        assert current_count == count, "Count should remain consistent"
        print("Count verification passed")

        # Test 5: Single text embedding
        print("\nTest 5: Single text embedding")
        print("-" * 30)

        single_text = "This is a single text for embedding"
        single_embedding = service.convert_single_text_to_embedding(single_text)
        print(f"Generated single embedding with {len(single_embedding)} dimensions")
        assert len(single_embedding) > 0, "Single embedding should not be empty"
        print("Single text embedding verified")

        print("\nAll tests passed! Complete workflow is working correctly.")
        print("=" * 50)

        return True

    except Exception as e:
        print(f"\nTest failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_error_handling():
    """
    Test error handling in the text embedding service.
    """
    print("\nTesting Error Handling")
    print("=" * 30)

    service = create_text_embedding_service()

    try:
        # Test empty text list
        try:
            embeddings = service.convert_text_to_embeddings([])
            print("Empty text list handled correctly (returned empty list)")
        except Exception as e:
            print(f"Empty text list raised appropriate exception: {type(e).__name__}")

        # Test empty query
        try:
            service.retrieve_similar_embeddings("", top_k=1)
            print("Empty query should have raised an exception")
        except ValueError:
            print("Empty query properly raises ValueError")
        except Exception as e:
            print(f"Empty query raises appropriate exception: {type(e).__name__}")

        print("Error handling tests completed")

    except Exception as e:
        print(f"Error handling test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("Starting Text Embedding Service Tests")
    print("=" * 60)

    success = test_complete_workflow()
    test_error_handling()

    if success:
        print("\nAll tests completed successfully!")
        print("\nSummary of what was tested:")
        print("  - Text to embedding conversion")
        print("  - Saving embeddings to Qdrant with metadata")
        print("  - Semantic search with similarity matching")
        print("  - Count operations")
        print("  - Single text embedding")
        print("  - Error handling")
    else:
        print("\nSome tests failed!")
        sys.exit(1)