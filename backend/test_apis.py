#!/usr/bin/env python3
"""
Test script to verify both Cohere and OpenAI API keys are working
"""
import os
from dotenv import load_dotenv
import cohere
from openai import OpenAI

# Load environment variables
load_dotenv()

# Test Cohere API
cohere_api_key = os.getenv('COHERE_API_KEY')
print(f"Cohere API key is set: {bool(cohere_api_key)}")

if cohere_api_key:
    try:
        cohere_client = cohere.Client(cohere_api_key)
        response = cohere_client.embed(
            texts=["test"],
            model="embed-english-v3.0",
            input_type="search_query"
        )
        print("✅ Cohere API is working correctly")
        print(f"   Embedding length: {len(response.embeddings[0])}")
    except Exception as e:
        print(f"❌ Error with Cohere API: {e}")
else:
    print("❌ Cohere API key is not set")

# Test OpenAI API
openai_api_key = os.getenv('OPENAI_API_KEY')
openai_base_url = os.getenv('OPENAI_BASE_URL', 'https://api.chatanywhere.org/v1')

print(f"\nOpenAI API key is set: {bool(openai_api_key)}")
print(f"OpenAI Base URL: {openai_base_url}")

if openai_api_key:
    try:
        client = OpenAI(
            api_key=openai_api_key,
            base_url=openai_base_url
        )

        # Test chat completion
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        print("✅ OpenAI API is working correctly")
        print(f"   Response: {response.choices[0].message.content[:50]}...")
    except Exception as e:
        print(f"❌ Error with OpenAI API: {e}")
else:
    print("❌ OpenAI API key is not set")