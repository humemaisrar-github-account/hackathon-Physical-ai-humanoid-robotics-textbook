"""
Debug Script for Embedding Save Issues

This script will help identify why embeddings are not being saved
and provide a working solution.
"""
import os
from dotenv import load_dotenv
import cohere
from qdrant_client import QdrantClient
from qdrant_client.http import models
from uuid import uuid4
from datetime import datetime

# Load environment variables explicitly
load_dotenv()

def test_embedding_save():
    """
    Test embedding save functionality step by step.
    """
    print("Debugging Embedding Save Issues")
    print("=" * 50)

    # Step 1: Check environment variables
    print("1. Checking environment variables...")
    cohere_api_key = os.getenv('COHERE_API_KEY')
    qdrant_url = os.getenv('QDRANT_URL')
    qdrant_api_key = os.getenv('QDRANT_API_KEY')

    if not cohere_api_key:
        print("   FAILED: COHERE_API_KEY not found in .env")
        return False
    else:
        print("   SUCCESS: COHERE_API_KEY found")

    if not qdrant_url:
        print("   FAILED: QDRANT_URL not found in .env")
        return False
    else:
        print("   SUCCESS: QDRANT_URL found:", qdrant_url)

    if not qdrant_api_key:
        print("   FAILED: QDRANT_API_KEY not found in .env")
        return False
    else:
        print("   SUCCESS: QDRANT_API_KEY found")

    # Step 2: Test Cohere connection
    print("\n2. Testing Cohere connection...")
    try:
        cohere_client = cohere.Client(cohere_api_key)
        print("   SUCCESS: Cohere client created successfully")

        # Test embedding generation
        test_text = "Test embedding for debugging"
        response = cohere_client.embed(
            texts=[test_text],
            model="embed-english-v3.0",
            input_type="search_document"
        )
        embedding = response.embeddings[0]
        print(f"   SUCCESS: Embedding generated successfully with size: {len(embedding)}")
        if len(embedding) != 1024:
            print(f"   FAILED: Embedding size is {len(embedding)}, expected 1024")
            return False
        else:
            print("   SUCCESS: Embedding size is correct (1024)")
    except Exception as e:
        print(f"   FAILED: Cohere test failed: {e}")
        return False

    # Step 3: Test Qdrant connection
    print("\n3. Testing Qdrant connection...")
    try:
        qdrant_client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key
        )
        print("   SUCCESS: Qdrant client created successfully")

        # Test basic connection
        collections = qdrant_client.get_collections()
        print(f"   SUCCESS: Qdrant connection successful, found {len(collections.collections)} collections")
    except Exception as e:
        print(f"   FAILED: Qdrant connection failed: {e}")
        if "404" in str(e) or "Not Found" in str(e):
            print("   INFO: This is likely a URL configuration issue")
            print("   INFO: Make sure your QDRANT_URL is correct")
            print("   INFO: Example: https://your-cluster-id.your-region.qdrant.tech:6333")
        return False

    # Step 4: Test collection creation
    print("\n4. Testing collection creation...")
    collection_name = "text_embeddings"
    try:
        # Check if collection exists
        collections = qdrant_client.get_collections()
        collection_exists = any(col.name == collection_name for col in collections.collections)

        if not collection_exists:
            # Create collection with required parameters
            qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=1024,
                    distance=models.Distance.COSINE
                ),
            )
            print(f"   SUCCESS: Collection '{collection_name}' created successfully")
        else:
            print(f"   SUCCESS: Collection '{collection_name}' already exists")
    except Exception as e:
        print(f"   FAILED: Collection creation failed: {e}")
        return False

    # Step 5: Test embedding save
    print("\n5. Testing embedding save...")
    try:
        # Generate embedding
        text_to_save = "This is a test text for embedding save functionality"
        metadata = {
            "category": "debug",
            "source": "test_save",
            "created_at": datetime.now().isoformat()
        }

        response = cohere_client.embed(
            texts=[text_to_save],
            model="embed-english-v3.0",
            input_type="search_document"
        )
        embedding = response.embeddings[0]

        # Create point
        vector_id = str(uuid4())
        point = models.PointStruct(
            id=vector_id,
            vector=embedding,
            payload={
                "text": text_to_save,
                "metadata": metadata,
                "original_text": text_to_save,
                **metadata
            }
        )

        # Upsert to Qdrant
        qdrant_client.upsert(
            collection_name=collection_name,
            points=[point]
        )

        print(f"   SUCCESS: Embedding saved successfully with ID: {vector_id}")

        # Check count after save
        count = qdrant_client.count(collection_name=collection_name)
        print(f"   SUCCESS: Collection now has {count.count} vectors")

    except Exception as e:
        print(f"   FAILED: Embedding save failed: {e}")
        return False

    # Step 6: Test retrieval
    print("\n6. Testing embedding retrieval...")
    try:
        query = "test text embedding"
        response = cohere_client.embed(
            texts=[query],
            model="embed-english-v3.0",
            input_type="search_query"
        )
        query_embedding = response.embeddings[0]

        # Search in Qdrant
        search_results = qdrant_client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=3,
            with_payload=True,
            with_vectors=False,
        )

        print(f"   SUCCESS: Found {len(search_results)} similar embeddings")
        for i, result in enumerate(search_results):
            print(f"     Result {i+1}: ID={result.id}, Score={result.score:.3f}")

    except Exception as e:
        print(f"   FAILED: Retrieval test failed: {e}")
        return False

    print("\n" + "=" * 50)
    print("SUCCESS: ALL TESTS PASSED!")
    print("SUCCESS: Embeddings are being saved and retrieved correctly!")
    print("SUCCESS: The collection and vectors should be visible in Qdrant dashboard")
    print("SUCCESS: Both save and retrieve functions are working")

    return True


def create_simple_save_function():
    """
    Create a simple, working save function that definitely works.
    """
    # Load environment
    load_dotenv()

    cohere_api_key = os.getenv('COHERE_API_KEY')
    qdrant_url = os.getenv('QDRANT_URL')
    qdrant_api_key = os.getenv('QDRANT_API_KEY')

    if not all([cohere_api_key, qdrant_url, qdrant_api_key]):
        raise ValueError("Missing required environment variables")

    # Create clients
    cohere_client = cohere.Client(cohere_api_key)
    qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
    collection_name = "text_embeddings"

    def save_embedding(text: str, metadata: dict) -> str:
        """Simple save function that definitely works."""
        try:
            # Generate embedding with correct model and size
            response = cohere_client.embed(
                texts=[text],
                model="embed-english-v3.0",
                input_type="search_document"
            )
            embedding = response.embeddings[0]

            if len(embedding) != 1024:
                raise ValueError(f"Expected 1024-dim embedding, got {len(embedding)}")

            # Create unique ID
            vector_id = str(uuid4())

            # Prepare payload
            payload = {
                "text": text,
                "created_at": datetime.now().isoformat(),
                **metadata
            }

            # Create and upsert point
            point = models.PointStruct(
                id=vector_id,
                vector=embedding,
                payload=payload
            )

            qdrant_client.upsert(
                collection_name=collection_name,
                points=[point]
            )

            print(f"Embedding saved successfully with ID: {vector_id}")
            return vector_id

        except Exception as e:
            print(f"Error saving embedding: {e}")
            raise

    return save_embedding


if __name__ == "__main__":
    success = test_embedding_save()

    if success:
        print("\nINFO: You can now use this simple save function:")
        print("""
def save_embedding(text: str, metadata: dict) -> str:
    # Load environment
    load_dotenv()
    cohere_api_key = os.getenv('COHERE_API_KEY')
    qdrant_url = os.getenv('QDRANT_URL')
    qdrant_api_key = os.getenv('QDRANT_API_KEY')

    # Create clients
    cohere_client = cohere.Client(cohere_api_key)
    qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)

    # Generate embedding
    response = cohere_client.embed(
        texts=[text],
        model="embed-english-v3.0",
        input_type="search_document"
    )
    embedding = response.embeddings[0]

    # Create unique ID
    vector_id = str(uuid4())

    # Prepare payload
    payload = {
        "text": text,
        "created_at": datetime.now().isoformat(),
        **metadata
    }

    # Create and upsert point
    point = models.PointStruct(
        id=vector_id,
        vector=embedding,
        payload=payload
    )

    qdrant_client.upsert(
        collection_name="text_embeddings",
        points=[point]
    )

    return vector_id
        """)
    else:
        print("\nFAILED: Tests failed - please check your .env configuration")
        print("Make sure QDRANT_URL is correct and Qdrant is accessible")