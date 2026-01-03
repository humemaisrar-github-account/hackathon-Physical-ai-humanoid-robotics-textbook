#!/usr/bin/env python3
"""
Simple runner for the RAG Chatbot Backend
"""
import uvicorn
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("Starting RAG Chatbot Backend...")
    print("Server will be available at: http://localhost:8001")
    print("Health check: http://localhost:8001/health")
    print("Chat endpoint: POST http://localhost:8001/api/v1/chat")

    uvicorn.run(
        "rag_chatbot:app",
        host="0.0.0.0",
        port=8001,  # Using port 8001 to avoid conflicts
        reload=False,  # Set to True for development
        log_level="info"
    )