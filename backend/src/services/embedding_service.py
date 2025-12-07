import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv() # Load environment variables

class EmbeddingService:
    def __init__(self, model: str = "models/embedding-001"): # Default to Gemini embedding model
        genai.configure(api_key=os.getenv("GEMINI_KEY")) # Ensure GEMINI_KEY is set in .env
        self.model = model

    def generate_embedding(self, text: str) -> list[float]:
        """
        Generates an embedding for the given text using Gemini's API.
        """
        if not text:
            return []
        try:
            response = genai.embed_content(
                model=self.model,
                content=text,
                task_type="RETRIEVAL_DOCUMENT" # Specify task type
            )
            return response['embedding']
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []

if __name__ == "__main__":
    # Example Usage:
    # Make sure to set GEMINI_KEY environment variable before running
    # os.environ["GEMINI_KEY"] = "YOUR_GEMINI_API_KEY"
    
    embedding_service = EmbeddingService(model=os.getenv("EMBEDDING_MODEL", "models/embedding-001"))
    text_to_embed = "This is a test sentence for embedding."
    embedding = embedding_service.generate_embedding(text_to_embed)
    print(f"Embedding length: {len(embedding)}")
    print(f"First 5 dimensions: {embedding[:5]}")