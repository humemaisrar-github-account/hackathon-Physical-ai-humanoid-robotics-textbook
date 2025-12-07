import os
import sys
from dotenv import load_dotenv
import chromadb
import uuid

# Add the parent directory of backend/src to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from src.services.rag_service import RAGService
from src.services.embedding_service import EmbeddingService
from src.services.vector_db_service import VectorDBService

load_dotenv() # Load environment variables from .env file

def main():
    docs_folder = os.getenv("DOCS_FOLDER", "../../website/docs") # Default to Docusaurus docs
    db_path = os.getenv("VECTOR_DB_PATH", "./chroma_db")
    
    # Initialize services
    rag_service = RAGService()
    embedding_service = EmbeddingService(model=os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002"))
    vector_db_service = VectorDBService(db_path=db_path)

    print(f"Loading and processing documents from: {docs_folder}")
    all_chunked_docs = rag_service.process_documents_for_rag(docs_folder)
    print(f"Total chunks generated: {len(all_chunked_docs)}")

    if not all_chunked_docs:
        print("No documents found or processed. Exiting.")
        return

    # Generate embeddings and prepare for storage
    documents_to_add = []
    for chunk in all_chunked_docs:
        embedding = embedding_service.generate_embedding(chunk["content"])
        if embedding:
            documents_to_add.append({
                "id": str(uuid.uuid5(uuid.NAMESPACE_URL, chunk["source_file"] + chunk["source_paragraph_id"])),
                "content": chunk["content"],
                "embedding": embedding,
                "metadata": {
                    "source_file": chunk["source_file"],
                    "source_paragraph_id": chunk["source_paragraph_id"]
                }
            })
    
    if not documents_to_add:
        print("No embeddings generated. Exiting.")
        return

    print(f"Adding {len(documents_to_add)} documents with embeddings to ChromaDB.")
    vector_db_service.add_documents(documents_to_add)
    print("Document ingestion complete.")

if __name__ == "__main__":
    main()
