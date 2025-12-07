from langchain.text_splitter import RecursiveCharacterTextSplitter
from pathlib import Path
from typing import List, Dict, Any
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class RAGService:
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )
        genai.configure(api_key=os.getenv("GEMINI_KEY"))
        self.chat_model = os.getenv("AGENT_MODEL", "gemini-1.5-flash") # Default to Gemini chat model
        self.model = genai.GenerativeModel(self.chat_model)

    def load_documents(self, docs_folder: str = "./website/docs"):
        """
        Loads all .md and .mdx documents from the specified folder.
        """
        documents = []
        for p in Path(docs_folder).rglob("*.md"):
            documents.append({"content": p.read_text(encoding='utf-8'), "source_file": str(p)})
        for p in Path(docs_folder).rglob("*.mdx"):
            documents.append({"content": p.read_text(encoding='utf-8'), "source_file": str(p)})
        return documents

    def chunk_document(self, document: Dict[str, Any]):
        """
        Chunks a single document into smaller pieces.
        """
        content = document["content"]
        source_file = document["source_file"]
        chunks = self.text_splitter.split_text(content)
        
        chunked_documents = []
        for i, chunk in enumerate(chunks):
            chunked_documents.append({
                "content": chunk,
                "source_file": source_file,
                "source_paragraph_id": f"{source_file}#{i}", # Simple ID for now
                "metadata": {"chunk_index": i}
            })
        return chunked_documents

    def process_documents_for_rag(self, docs_folder: str = "./website/docs"):
        """
        Loads and chunks all documents, returning a list of chunked documents.
        """
        loaded_docs = self.load_documents(docs_folder)
        all_chunked_docs = []
        for doc in loaded_docs:
            all_chunked_docs.extend(self.chunk_document(doc))
        return all_chunked_docs

    def generate_response(self, user_query: str, context_chunks: List[Dict[str, Any]], selected_text: str = None):
        """
        Generates a chatbot response based on user query and retrieved context chunks, supporting streaming.
        """
        # Gemini does not have explicit "system" role in the same way OpenAI does.
        # The system instructions are typically woven into the initial prompt or via tools.
        # For a simple RAG, we can prepend context to the user query.

        system_instruction = "You are a helpful assistant for the 'Humanoid Physical AI Book'. Answer questions strictly based on the provided context. If the answer is not in the context, state 'Not found in the book.' Do not generate opinions or external knowledge."
        
        if selected_text:
            system_instruction += f"\nPrioritize answering from this selected text: {selected_text}"

        context_str = "\n\n".join([chunk["content"] for chunk in context_chunks])
        
        full_query = f"{system_instruction}\n\nContext from book:\n{context_str}\n\nUser query: {user_query}"

        try:
            # Gemini's generate_content directly streams if configured
            response_stream = self.model.generate_content(
                full_query,
                stream=True
            )
            return response_stream # Return the stream directly
        except Exception as e:
            print(f"Error generating chat response: {e}")
            raise

if __name__ == "__main__":
    # Example Usage for RAG query logic (requires embedding_service and vector_db_service setup)
    # Make sure to set GEMINI_KEY environment variable
    # os.environ["GEMINI_KEY"] = "YOUR_GEMINI_API_KEY"
    # os.environ["AGENT_MODEL"] = "gemini-1.5-flash"

    rag_service = RAGService()
    
    mock_query = "What is ROS used for?"
    mock_context_chunks = [
        {"content": "ROS (Robot Operating System) is a flexible framework for writing robot software. It is a collection of tools, libraries, and conventions that aim to simplify the task of creating complex and robust robot behavior across a wide variety of robotic platforms.", 
         "source_file": "docs/ros.md", "source_paragraph_id": "docs/ros.md#0"}
    ]
    
    response_stream = rag_service.generate_response(mock_query, mock_context_chunks)
    print("\nGenerated Response Stream Example:")
    for chunk in response_stream:
        print(chunk.text, end="")
    print("\n")

    # Example for document processing
    docs = rag_service.process_documents_for_rag(docs_folder="../../website/docs")
    print(f"\nProcessed {len(docs)} chunks from website/docs.")