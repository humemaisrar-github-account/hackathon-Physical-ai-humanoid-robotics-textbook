"""
Example usage of the Text Embedding Service.

This script demonstrates how to use the text embedding functionality
that was implemented according to your requirements.
"""
import asyncio
import os
import sys
from typing import List, Dict, Any

# Add the backend/src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from src.services.text_embedding_service import create_text_embedding_service


def example_usage():
    """
    Example usage of the text embedding service.
    """
    print("Example Usage of Text Embedding Service")
    print("=" * 45)

    # Create the service
    service = create_text_embedding_service()

    # Example 1: Convert text to embeddings
    print("\n1. Converting text to embeddings:")
    print("-" * 35)

    texts = [
        "The future of artificial intelligence is promising",
        "Machine learning algorithms are becoming more sophisticated",
        "Natural language processing enables human-computer interaction"
    ]

    # Generate embeddings
    embeddings = service.convert_text_to_embeddings(texts)
    print(f"Generated {len(embeddings)} embeddings")
    print(f"Each embedding has {len(embeddings[0])} dimensions")

    # Example 2: Save embeddings to Qdrant (with mocked success)
    print("\n2. Saving embeddings to Qdrant:")
    print("-" * 32)

    metadata = [
        {"category": "AI", "source": "example", "topic": "future"},
        {"category": "ML", "source": "example", "topic": "algorithms"},
        {"category": "NLP", "source": "example", "topic": "interaction"}
    ]

    # In a real scenario, this would save to Qdrant
    # For this example, we'll show what would happen
    print("Embeddings would be saved to Qdrant with the following structure:")
    for i, (text, meta) in enumerate(zip(texts, metadata)):
        print(f"  - ID: auto-generated UUID")
        print(f"    Text: '{text[:50]}...'")
        print(f"    Metadata: {meta}")
        print(f"    Vector: {len(embeddings[i])}-dimensional embedding")

    # Example 3: Retrieve similar embeddings
    print("\n3. Retrieving similar embeddings:")
    print("-" * 37)

    query = "advancements in artificial intelligence"

    # In a real scenario, this would search in Qdrant
    # For this example, we'll show the expected interface
    print(f"Query: '{query}'")
    print("This would return similar embeddings from Qdrant with:")
    print("  - IDs of similar documents")
    print("  - Similarity scores")
    print("  - Original text content")
    print("  - Associated metadata")

    # Example 4: Single text embedding
    print("\n4. Single text embedding:")
    print("-" * 26)

    single_text = "Python is great for machine learning"
    single_embedding = service.convert_single_text_to_embedding(single_text)
    print(f"Text: '{single_text}'")
    print(f"Embedding: {len(single_embedding)}-dimensional vector")


def api_usage_examples():
    """
    Examples of how to use the API endpoints.
    """
    print("\n\nAPI Usage Examples")
    print("=" * 18)

    print("\nPOST /api/v1/embed - Convert texts to embeddings:")
    print("Request:")
    print('  {')
    print('    "texts": ["text1", "text2", "text3"]')
    print('  }')
    print("Response:")
    print('  {')
    print('    "success": true,')
    print('    "message": "Successfully generated 3 embeddings",')
    print('    "embeddings": [[0.1, 0.2, ...], [0.3, 0.4, ...], ...],')
    print('    "count": 3')
    print('  }')

    print("\nPOST /api/v1/save - Save embeddings to Qdrant:")
    print("Request:")
    print('  {')
    print('    "texts": ["text1", "text2"],')
    print('    "metadata_list": [')
    print('      {"category": "AI", "source": "example"},')
    print('      {"category": "ML", "source": "example"}')
    print('    ]')
    print('  }')
    print("Response:")
    print('  {')
    print('    "success": true,')
    print('    "message": "Successfully saved 2 embeddings to Qdrant",')
    print('    "ids": ["id1", "id2"],')
    print('    "count": 2')
    print('  }')

    print("\nPOST /api/v1/search - Search for similar embeddings:")
    print("Request:")
    print('  {')
    print('    "query_text": "artificial intelligence",')
    print('    "top_k": 5')
    print('  }')
    print("Response:")
    print('  {')
    print('    "success": true,')
    print('    "message": "Successfully found 3 similar embeddings",')
    print('    "results": [')
    print('      {')
    print('        "id": "embedding_id",')
    print('        "score": 0.95,')
    print('        "text": "original text content",')
    print('        "payload": {"category": "AI", "source": "example"}')
    print('      }')
    print('    ],')
    print('    "query_text": "artificial intelligence"')
    print('  }')


if __name__ == "__main__":
    print("Text Embedding Service - Implementation Overview")
    print("=" * 50)
    print("\nThis implementation provides:")
    print("✓ Text to embedding conversion using Cohere")
    print("✓ Saving embeddings to Qdrant with metadata")
    print("✓ Similarity search to retrieve relevant embeddings")
    print("✓ REST API endpoints for all operations")
    print("✓ Proper error handling and validation")

    example_usage()
    api_usage_examples()

    print("\n" + "=" * 50)
    print("Implementation Summary:")
    print("- Created TextEmbeddingService class in backend/src/services/text_embedding_service.py")
    print("- Added API endpoints in backend/src/api/v1/text_embedding.py")
    print("- Integrated with main application in backend/src/main.py")
    print("- Provided comprehensive functionality for text embedding operations")