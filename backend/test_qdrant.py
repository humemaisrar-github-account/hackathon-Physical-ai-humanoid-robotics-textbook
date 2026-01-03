#!/usr/bin/env python3
"""
Test script to check Qdrant collection and embeddings
"""
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models
import cohere

# Load environment variables
load_dotenv()

# Initialize clients
qdrant_client = QdrantClient(
    url=os.getenv('QDRANT_URL'),
    api_key=os.getenv('QDRANT_API_KEY')
)

cohere_client = cohere.Client(os.getenv('COHERE_API_KEY'))

# Check collection info
collection_name = "text_embeddings"
collection_info = qdrant_client.get_collection(collection_name)
print(f"Collection: {collection_name}")
print(f"Vector size: {collection_info.config.params.vectors.size}")
print(f"Distance: {collection_info.config.params.vectors.distance}")
print(f"Total vectors: {collection_info.points_count}")

# Get a sample point to see the payload structure
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

    # Test embedding generation
    test_text = "artificial intelligence"
    response = cohere_client.embed(
        texts=[test_text],
        model="embed-english-v3.0",
        input_type="search_query"
    )
    query_embedding = response.embeddings[0]
    print(f"\nQuery embedding length: {len(query_embedding)}")

    # Test search
    search_results = qdrant_client.query_points(
        collection_name=collection_name,
        query=query_embedding,
        limit=3,
        with_payload=True,
        with_vectors=False,
    )

    print(f"\nSearch results count: {len(search_results.points)}")
    for i, point in enumerate(search_results.points):
        print(f"Result {i+1}: Score={point.score}, Payload keys={list(point.payload.keys())}")
        if 'text' in point.payload:
            print(f"  Text: {point.payload['text'][:100]}...")
        if 'content' in point.payload:
            print(f"  Content: {point.payload['content'][:100]}...")
else:
    print("No points found in the collection")