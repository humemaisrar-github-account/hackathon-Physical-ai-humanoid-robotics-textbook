from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import List, Optional, AsyncIterable
from ..services.rag_service import RAGService
from ..services.embedding_service import EmbeddingService
from ..services.vector_db_service import VectorDBService
from ..models.chat_model import ChatMessage, UserMessage, BotResponse, Citation # Import models
import uuid
import json

router = APIRouter()

# Initialize services (these should ideally be dependency injected in a real app)
rag_service = RAGService()
embedding_service = EmbeddingService()
vector_db_service = VectorDBService()

class DocumentChunkModel(BaseModel): # Renamed to avoid conflict with DocumentChunk in rag_model
    content: str
    source_file: str
    source_paragraph_id: Optional[str] = None

class EmbedDocumentsRequest(BaseModel):
    documents: List[DocumentChunkModel]

@router.post("/embed", summary="Generate and store embeddings for document chunks")
async def embed_documents(request: EmbedDocumentsRequest):
    if not request.documents:
        raise HTTPException(status_code=400, detail="No documents provided for embedding.")
    
    processed_docs_for_db = []
    for doc_chunk in request.documents:
        # Generate embedding for the content
        embedding = embedding_service.generate_embedding(doc_chunk.content)
        if not embedding:
            raise HTTPException(status_code=500, detail=f"Failed to generate embedding for document from {doc_chunk.source_file}")
        
        # Prepare document for vector DB
        doc_id = str(uuid.uuid4()) # Generate a unique ID for each chunk
        processed_docs_for_db.append({
            "id": doc_id,
            "content": doc_chunk.content,
            "embedding": embedding,
            "metadata": {
                "source_file": doc_chunk.source_file,
                "source_paragraph_id": doc_chunk.source_paragraph_id
            }
        })
    
    try:
        vector_db_service.add_documents(processed_docs_for_db)
        return {"message": f"Embeddings generated and stored for {len(processed_docs_for_db)} documents."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store embeddings: {str(e)}")

async def generate_response_stream(user_message: UserMessage) -> AsyncIterable[str]:
    # 1. Retrieve relevant chunks based on user_message.message or user_message.selected_text
    query_text = user_message.selected_text if user_message.selected_text else user_message.message
    
    if not query_text:
        yield json.dumps({"error": "Message or selected text is required."}) + "\n"
        return

    # Generate embedding for the query
    query_embedding = embedding_service.generate_embedding(query_text)
    if not query_embedding:
        yield json.dumps({"error": "Failed to generate query embedding."}) + "\n"
        return

    # Query vector DB for relevant context
    retrieved_results = vector_db_service.query_documents(query_embeddings=[query_embedding], n_results=5)
    
    context_chunks = []
    if retrieved_results and retrieved_results["documents"]:
        for i, doc_content in enumerate(retrieved_results["documents"][0]):
            metadata = retrieved_results["metadatas"][0][i]
            context_chunks.append({
                "content": doc_content,
                "source_file": metadata.get("source_file"),
                "source_paragraph_id": metadata.get("source_paragraph_id")
            })

    # 2. Generate streaming response using RAGService
    try:
        response_stream = rag_service.generate_response(user_message.message, context_chunks, user_message.selected_text)
        
        full_response_content = ""
        citations_collected = []

        for chunk in response_stream:
            delta_content = chunk.choices[0].delta.content
            if delta_content:
                full_response_content += delta_content
                yield json.dumps({"type": "delta", "content": delta_content}) + "\n"
            
            # OpenAI streaming responses don't include citations until the end (or not at all via stream)
            # For simplicity, citations will be sent as a final message after the stream
            # In a more complex setup, citations might be determined before streaming starts or sent as separate stream events.

        # After the stream ends, determine and send citations
        final_citations = []
        for c_chunk in context_chunks:
            final_citations.append(Citation(
                source_file=c_chunk["source_file"],
                paragraph_reference=c_chunk["source_paragraph_id"],
                text_excerpt=c_chunk["content"][:100] + "..."
            ).dict()) # Convert to dict for JSON serialization
        
        yield json.dumps({"type": "end", "citations": final_citations}) + "\n"


    except Exception as e:
        print(f"Error during streaming chat response: {e}")
        yield json.dumps({"error": "An error occurred during response generation."}) + "\n"

@router.post("/chat", summary="Send a message to the chatbot and get a response")
async def chat(user_message: UserMessage):
    return StreamingResponse(generate_response_stream(user_message), media_type="text/event-stream")


@router.get("/health", summary="Health check endpoint")
async def health_check():
    # In a real application, you'd check database connections, external services, etc.
    return {"status": "ok"}
