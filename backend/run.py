#!/usr/bin/env python3
"""
Application runner for the RAG Agent service.

This script provides a simple way to run the FastAPI application using uvicorn.
It loads the configuration from the settings module and starts the server.
"""

import uvicorn
from src.config.settings import settings


def run_server():
    """Run the FastAPI application using uvicorn."""
    uvicorn.run(
        "src.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True,  # Enable auto-reload during development
        log_level="info"
    )


if __name__ == "__main__":
    run_server()