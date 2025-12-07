import pytest
from fastapi.testclient import TestClient
from backend.main import app
from unittest.mock import patch, MagicMock
import os
import json
import uuid
import google.generativeai as genai # Import for mocking

# Fixture for the TestClient
@pytest.fixture(scope="module")
def client():
    # Set environment variables for testing
    with patch.dict(os.environ, {
        "GEMINI_KEY": "test_gemini_key",
        "EMBEDDING_MODEL": "gemini-embedding-001",
        "AGENT_MODEL": "gemini-1.5-flash",
        "VECTOR_DB_PATH": "./test_chroma_db_integration"
    }):
        with TestClient(app) as c:
            yield c
    # Clean up any test artifacts if necessary
    if os.path.exists("./test_chroma_db_integration"):
        import shutil
        shutil.rmtree("./test_chroma_db_integration")

# Mock the external services (Gemini and ChromaDB) for integration tests
@pytest.fixture(autouse=True)
def mock_services():
    with patch("backend.src.services.embedding_service.genai") as mock_gemini_embed, \
         patch("backend.src.services.rag_service.genai") as mock_gemini_chat, \
         patch("backend.src.services.vector_db_service.VectorDBService") as mock_vector_db_service_class: # Mock the class
        
        # Mock EmbeddingService.generate_embedding
        mock_gemini_embed.embed_content.return_value = {'embedding': [0.1]*1536}

        # Mock RAGService.generate_response for streaming
        mock_response_stream = [
            MagicMock(text="Hello "), 
            MagicMock(text="there!"),
            MagicMock(text=" This is a Gemini response.")
        ]
        mock_generative_model = MagicMock()
        mock_generative_model.generate_content.return_value = mock_response_stream
        mock_gemini_chat.GenerativeModel.return_value = mock_generative_model

        # Mock VectorDBService instance methods
        mock_vector_db_service_instance = MagicMock()
        mock_vector_db_service_instance.add_documents.return_value = None
        mock_vector_db_service_instance.query_documents.return_value = {
            "documents": [["Relevant document chunk content."]],
            "metadatas": [[{"source_file": "test.md", "source_paragraph_id": "test.md#0"}]],
            "ids": [["doc_id_1"]]
        }
        mock_vector_db_service_instance.query_texts.return_value = { # Also mock query_texts if used
            "documents": [["Relevant document chunk content."]],
            "metadatas": [[{"source_file": "test.md", "source_paragraph_id": "test.md#0"}]],
            "ids": [["doc_id_1"]]
        }
        mock_vector_db_service_class.return_value = mock_vector_db_service_instance # Return the mocked instance
        
        yield

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_embed_documents(client):
    document = {
        "content": "This is a test document.",
        "source_file": "test.md",
        "source_paragraph_id": "test_p1"
    }
    response = client.post("/embed", json={"documents": [document]})
    assert response.status_code == 200
    assert "Embeddings generated and stored for 1 documents." in response.json()["message"]

def test_chat_streaming(client):
    conversation_id = str(uuid.uuid4())
    message_payload = {
        "conversation_id": conversation_id,
        "message": "What is the capital of France?"
    }
    
    response = client.post("/chat", json=message_payload)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream"
    
    full_response_content = ""
    citations_received = []
    
    for line in response.iter_lines():
        if line:
            # FastAPI's StreamingResponse yields bytes, so decode
            line_str = line.decode("utf-8")
            if line_str.startswith("data: "):
                try:
                    data = json.loads(line_str[len("data: "):])
                    if data.get("type") == "delta":
                        full_response_content += data.get("content", "")
                    elif data.get("type") == "end":
                        citations_received = data.get("citations", [])
                except json.JSONDecodeError:
                    pytest.fail(f"Could not decode JSON from line: {line_str}")
    
    assert "Hello there! This is a Gemini response." in full_response_content # From mock_gemini_chat
    assert len(citations_received) > 0
    assert "source_file" in citations_received[0]
