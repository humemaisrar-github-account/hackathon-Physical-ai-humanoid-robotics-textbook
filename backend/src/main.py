from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config.settings import settings
from src.middleware import logging_middleware


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.api_title,
        description=settings.api_description,
        version=settings.api_version,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify exact origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add custom logging middleware
    app.middleware("http")(logging_middleware)

    @app.on_event("shutdown")
    async def shutdown_event():
        """Handle application shutdown."""
        print("Shutting down RAG Agent API...")

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    # Include API routes
    from src.api.v1.query import router as query_router
    app.include_router(query_router, prefix="/api/v1", tags=["query"])

    from src.api.v1.text_embedding import router as text_embedding_router
    app.include_router(text_embedding_router, prefix="/api/v1", tags=["text_embedding"])

    from src.api.v1.chat import router as chat_router
    app.include_router(chat_router, prefix="/api/v1", tags=["chat"])

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True
    )