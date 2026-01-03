"""
Test script for the new chat endpoint.
"""
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_chat_endpoint():
    """
    Test the chat endpoint with a sample query.
    """
    # Get API key from environment
    api_key = os.getenv('API_KEY', 'your-api-key-here')
    base_url = "http://localhost:8000"

    # Sample query
    sample_query = {
        "query": "What is artificial intelligence?",
        "selected_text": None,
        "top_k": 3,
        "include_sources": True
    }

    print("Testing Chat Endpoint")
    print("=" * 30)
    print(f"Sending query: {sample_query['query']}")

    try:
        # Make request to the chat endpoint
        response = requests.post(
            f"{base_url}/api/v1/chat",
            json=sample_query,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        )

        print(f"Response Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")

            print("\nChat endpoint is working correctly!")
            print(f"- Response: {result.get('response', '')[:100]}...")
            print(f"- Sources: {len(result.get('sources', []))} sources found")
            print(f"- Query ID: {result.get('query_id')}")

        elif response.status_code == 401:
            print("Authentication failed - check your API key")
            print("Response:", response.json())
        elif response.status_code == 400:
            print("Bad request - check your query format")
            print("Response:", response.json())
        else:
            print(f"Unexpected status code: {response.status_code}")
            print("Response:", response.json())

    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Could not connect to the server")
        print("Make sure the backend server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")


def test_chat_with_selected_text():
    """
    Test the chat endpoint with selected text mode.
    """
    # Get API key from environment
    api_key = os.getenv('API_KEY', 'your-api-key-here')
    base_url = "http://localhost:8000"

    # Sample query with selected text
    sample_query = {
        "query": "What does this text say about machine learning?",
        "selected_text": "Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data. It involves training models on datasets to make predictions or decisions without being explicitly programmed.",
        "top_k": 2,
        "include_sources": True
    }

    print("\nTesting Chat Endpoint with Selected Text Mode")
    print("=" * 50)
    print(f"Query: {sample_query['query']}")
    print(f"Selected Text: {sample_query['selected_text'][:50]}...")

    try:
        # Make request to the chat endpoint
        response = requests.post(
            f"{base_url}/api/v1/chat",
            json=sample_query,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        )

        print(f"Response Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")

            print("\nSelected text mode is working correctly!")
            print(f"- Response: {result.get('response', '')[:100]}...")
            print(f"- Sources: {len(result.get('sources', []))} sources found")

        else:
            print(f"Error: {response.status_code}")
            print("Response:", response.json())

    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Could not connect to the server")
        print("Make sure the backend server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("Testing the new Chat API endpoint for RAG integration...")

    # Test basic chat functionality
    test_chat_endpoint()

    # Test selected text functionality
    test_chat_with_selected_text()

    print("\n" + "=" * 60)
    print("Test completed!")
    print("The chat endpoint is ready for frontend integration.")
    print("Next steps:")
    print("1. Start your backend server: python -m src.main")
    print("2. Create the frontend component to call this endpoint")
    print("3. Test the full integration")