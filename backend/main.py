import uvicorn
import logging
import sys
from fastapi import FastAPI, HTTPException # Corrected: import HTTPException from fastapi
from fastapi.responses import JSONResponse # Added: import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from src.api.endpoints import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Humanoid Assistant Chatbot API",
    description="API for the RAG-based AI Chatbot integrated into the Humanoid Physical AI Book.",
    version="1.0.0"
)

# CORS configuration
origins = [
    "http://localhost",
    "http://localhost:3000",  # Docusaurus default port
    "http://localhost:8000",  # FastAPI default port if frontend served from here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# Global exception handler for HTTPException
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
    )

# Global exception handler for unexpected errors
@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    logger.exception(f"Unhandled Exception: {exc}") # Log the full traceback
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected server error occurred."}
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
