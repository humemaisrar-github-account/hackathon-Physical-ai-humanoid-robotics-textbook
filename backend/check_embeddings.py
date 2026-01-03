#!/usr/bin/env python3
"""
Script to check the current embeddings in the Qdrant database
"""
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

# Load environment variables
load_dotenv()

# Initialize Qdrant client
qdrant_client = QdrantClient(
    url=os.getenv('QDRANT_URL'),
    api_key=os.getenv('QDRANT_API_KEY')
)

# Get collection info
collection_name = "text_embeddings"
collection_info = qdrant_client.get_collection(collection_name)
print(f"Collection: {collection_name}")
print(f"Vector size: {collection_info.config.params.vectors.size}")
print(f"Distance: {collection_info.config.params.vectors.distance}")
print(f"Total vectors: {collection_info.points_count}")

# Get a sample point to see the payload structure
try:
    points = qdrant_client.scroll(
        collection_name=collection_name,
        limit=1,
        with_payload=True,
        with_vectors=False
    )

    if points[0]:
        sample_point = points[0][0]
        print(f"\nSample point ID: {sample_point.id}")
        print(f"Sample payload: {sample_point.payload}")
    else:
        print("No points found in the collection")
except Exception as e:
    print(f"Error accessing collection: {e}")