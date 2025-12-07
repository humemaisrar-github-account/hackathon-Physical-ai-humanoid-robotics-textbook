import pytest
from unittest.mock import MagicMock, patch
from backend.src.services.rag_service import RAGService
import os
import google.generativeai as genai # Import for mocking

# Mock os.getenv for environment variables
@pytest.fixture(autouse=True)
def mock_env_vars():
    with patch.dict(os.environ, {
        "GEMINI_KEY": "test_gemini_key",
        "AGENT_MODEL": "gemini-1.5-flash",
        "EMBEDDING_MODEL": "gemini-embedding-001"
    }):
        yield

# Fixture for RAGService instance
@pytest.fixture
def rag_service():
    return RAGService()

# Test cases for load_documents
def test_load_documents_md_and_mdx(rag_service, tmp_path):
    # Create dummy markdown files
    (tmp_path / "doc1.md").write_text("Content of doc1.md")
    (tmp_path / "doc2.mdx").write_text("Content of doc2.mdx")
    
    docs = rag_service.load_documents(str(tmp_path))
    assert len(docs) == 2
    assert any("doc1.md" in d["source_file"] for d in docs)
    assert any("doc2.mdx" in d["source_file"] for d in docs)

def test_load_documents_empty_folder(rag_service, tmp_path):
    docs = rag_service.load_documents(str(tmp_path))
    assert len(docs) == 0

# Test cases for chunk_document
def test_chunk_document_basic(rag_service):
    doc = {"content": "This is a sentence. This is another sentence.", "source_file": "test.md"}
    chunks = rag_service.chunk_document(doc)
    assert len(chunks) >= 1
    assert "content" in chunks[0]
    assert "source_file" in chunks[0]
    assert "source_paragraph_id" in chunks[0]

def test_chunk_document_long_text(rag_service):
    long_text = "a" * 2000 # Longer than default chunk_size (800)
    doc = {"content": long_text, "source_file": "long.md"}
    chunks = rag_service.chunk_document(doc)
    assert len(chunks) > 1 # Should be split into multiple chunks

# Test cases for generate_response
@patch("backend.src.services.rag_service.genai.GenerativeModel")
def test_generate_response_basic(mock_generative_model, rag_service):
    # Mock Gemini chat completion
    mock_response_stream = [MagicMock(text="Mocked response part 1"), MagicMock(text="Mocked response part 2")]
    mock_generative_model.return_value.generate_content.return_value = mock_response_stream

    user_query = "What is ROS?"
    context_chunks = [
        {"content": "ROS is Robot Operating System.", "source_file": "ros.md", "source_paragraph_id": "ros.md#0"}
    ]
    
    response_stream = rag_service.generate_response(user_query, context_chunks)
    
    # Assert that the Gemini API was called
    mock_generative_model.return_value.generate_content.assert_called_once()
    assert mock_generative_model.return_value.generate_content.call_args[1]["stream"] is True

def test_generate_response_no_context(rag_service):
    user_query = "What is ROS?"
    context_chunks = []
    
    @patch("backend.src.services.rag_service.genai.GenerativeModel")
    def inner_test(mock_generative_model):
        mock_response_stream = [MagicMock(text="Not found in the book.")]
        mock_generative_model.return_value.generate_content.return_value = mock_response_stream

        response_stream = rag_service.generate_response(user_query, context_chunks)
        
        full_response = ""
        for chunk in response_stream:
            full_response += chunk.text if chunk.text else ""
        
        assert "Not found in the book" in full_response
        
    inner_test()

def test_process_documents_for_rag(rag_service, tmp_path):
    (tmp_path / "test.md").write_text("Line 1.\nLine 2.\nLine 3.")
    processed_docs = rag_service.process_documents_for_rag(str(tmp_path))
    assert len(processed_docs) >= 1
    assert "content" in processed_docs[0]
    assert "source_file" in processed_docs[0]