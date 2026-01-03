#!/usr/bin/env python3
"""
Test script to verify the new Cohere API key is working
"""
import os
from dotenv import load_dotenv
import cohere

# Load environment variables
load_dotenv()

# Initialize Cohere client
cohere_api_key = os.getenv('COHERE_API_KEY')
print(f"COHERE_API_KEY is set: {bool(cohere_api_key)}")

if cohere_api_key:
    try:
        cohere_client = cohere.Client(cohere_api_key)

        # Test embedding
        test_text = "test query"
        print(f"Testing embedding for: {test_text}")

        response = cohere_client.embed(
            texts=[test_text],
            model="embed-english-v3.0",
            input_type="search_query"
        )

        embedding = response.embeddings[0]
        print(f"Success! Embedding generated with length: {len(embedding)}")
        print("Cohere API key is working correctly.")

    except Exception as e:
        print(f"Error with Cohere API: {e}")
else:
    print("COHERE_API_KEY is not set in the environment")