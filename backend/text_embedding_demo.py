"""
Text Embedding Service Demo

This script demonstrates the complete functionality for:
1. Converting text to embeddings using Cohere
2. Saving embeddings to Qdrant with appropriate IDs and metadata
3. Retrieving the most relevant embeddings from Qdrant based on similarity search
"""
import asyncio
import sys
import os
from typing import List, Dict, Any
import logging

# Add the backend/src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.text_embedding_service import create_text_embedding_service

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def demo_text_to_embeddings():
    """
    Demonstrate converting text to embeddings using Cohere.
    """
    print("1. Converting Text to Embeddings")
    print("=" * 40)

    # Create the service
    service = create_text_embedding_service()

    # Sample texts to convert to embeddings
    sample_texts = [
        "The future of artificial intelligence is promising with many advancements in machine learning",
        "Machine learning algorithms are becoming more sophisticated and efficient",
        "Natural language processing enables computers to understand human language",
        "Vector databases like Qdrant store embeddings for efficient similarity search",
        "Retrieval-Augmented Generation (RAG) combines retrieval and generation for better responses"
    ]

    print(f"Converting {len(sample_texts)} texts to embeddings...")

    # Convert texts to embeddings
    embeddings = service.convert_text_to_embeddings(sample_texts)

    print(f"SUCCESS: Successfully generated {len(embeddings)} embeddings")
    print(f"SUCCESS: Each embedding has {len(embeddings[0])} dimensions")

    # Show a sample embedding (first 10 dimensions)
    print(f"SUCCESS: Sample embedding (first 10 dims): {embeddings[0][:10]}...")

    print()
    return service, sample_texts, embeddings


def demo_save_to_qdrant(service, texts: List[str], embeddings: List[List[float]]):
    """
    Demonstrate saving embeddings to Qdrant with appropriate IDs and metadata.
    """
    print("2. Saving Embeddings to Qdrant")
    print("=" * 40)

    # Sample metadata for each text
    sample_metadata = [
        {"category": "AI", "source": "demo", "topic": "future"},
        {"category": "ML", "source": "demo", "topic": "algorithms"},
        {"category": "NLP", "source": "demo", "topic": "language"},
        {"category": "Databases", "source": "demo", "topic": "vector"},
        {"category": "RAG", "source": "demo", "topic": "retrieval"}
    ]

    print(f"Saving {len(texts)} embeddings to Qdrant with metadata...")

    # Save embeddings to Qdrant
    saved_ids = service.save_embeddings_to_qdrant(texts, sample_metadata)

    print(f"SUCCESS: Successfully saved {len(saved_ids)} embeddings to Qdrant")
    print(f"SUCCESS: Saved with IDs: {saved_ids}")

    # Get the total count of embeddings in the collection
    count = service.get_embedding_count()
    print(f"SUCCESS: Total embeddings in collection: {count}")

    print()
    return saved_ids


def demo_retrieve_similar(service, query_text: str):
    """
    Demonstrate retrieving the most relevant embeddings from Qdrant based on similarity search.
    """
    print("3. Retrieving Similar Embeddings")
    print("=" * 40)

    print(f"Searching for embeddings similar to: '{query_text}'")

    # Retrieve similar embeddings
    similar_results = service.retrieve_similar_embeddings(query_text, top_k=3)

    print(f"SUCCESS: Found {len(similar_results)} similar embeddings:")

    for i, result in enumerate(similar_results, 1):
        print(f"  {i}. ID: {result['id']}")
        print(f"     Score: {result['score']:.3f}")
        print(f"     Text: '{result['text'][:60]}...'")
        print(f"     Metadata: {result['payload']}")
        print()

    print()
    return similar_results


def demo_single_text_embedding(service):
    """
    Demonstrate converting a single text to embedding.
    """
    print("4. Single Text Embedding")
    print("=" * 40)

    single_text = "Deep learning neural networks are powerful"
    print(f"Converting single text: '{single_text}'")

    # Convert single text to embedding
    single_embedding = service.convert_single_text_to_embedding(single_text)

    print(f"SUCCESS: Successfully generated embedding with {len(single_embedding)} dimensions")
    print(f"SUCCESS: Sample (first 10 dims): {single_embedding[:10]}...")
    print()


def main():
    """
    Main function to run the complete demo.
    """
    print("Text Embedding Service Demo")
    print("=" * 50)
    print("This demo shows how to:")
    print("1. Convert text to embeddings using Cohere")
    print("2. Save embeddings to Qdrant with metadata")
    print("3. Retrieve similar embeddings based on similarity search")
    print("4. Handle single text embedding")
    print()

    try:
        # Step 1: Convert text to embeddings
        service, sample_texts, embeddings = demo_text_to_embeddings()

        # Step 2: Save embeddings to Qdrant
        saved_ids = demo_save_to_qdrant(service, sample_texts, embeddings)

        # Step 3: Retrieve similar embeddings
        demo_retrieve_similar(service, "artificial intelligence and machine learning")

        # Step 4: Single text embedding
        demo_single_text_embedding(service)

        print("Demo Summary:")
        print("- Text to embedding conversion: SUCCESS")
        print("- Saving to Qdrant with metadata: SUCCESS")
        print("- Similarity search: SUCCESS")
        print("- Single text embedding: SUCCESS")
        print()
        print("All operations completed successfully!")

    except Exception as e:
        logger.error(f"Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Demo completed successfully!")
    else:
        print("\n❌ Demo failed!")
        sys.exit(1)