"""Main FastAPI application - Refactored for Modular Monolith."""
import logging
import time
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from middleware.common import RequestIDMiddleware, LoggingMiddleware
from api.deps import get_chat_service, get_document_service, get_llm
from schemas.chat import HealthResponse
from routers import chat, documents

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rag-api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    logger.info("=" * 60)
    logger.info(f"[*] Starting {settings.project_name} v{settings.version}")
    logger.info("=" * 60)
    
    # Pre-warm/Validate LLM
    llm = get_llm()
    status = llm.validate_setup()
    if not status.get('ollama_running'):
        logger.warning("[!] Ollama is not running!")
    
    yield
    logger.info("[*] Shutting down...")

app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    lifespan=lifespan
)

# Middleware
app.add_middleware(RequestIDMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(chat.router)
app.include_router(documents.router)

@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.project_name} 🚀",
        "version": settings.version,
        "status": "Running"
    }

@app.get("/api/health", response_model=HealthResponse)
async def health_check(service=Depends(get_document_service), llm=Depends(get_llm)):
    llm_status = llm.validate_setup()
    stats = service.get_stats()
    
    is_healthy = llm_status.get('ollama_running') and stats.get('total_documents', 0) > 0
    
    return HealthResponse(
        status="healthy" if is_healthy else "degraded",
        ollama_running=llm_status.get('ollama_running', False),
        model_available=llm_status.get('model_available', False),
        vectorstore_initialized=stats.get('total_documents', 0) > 0,
        configured_model=settings.ollama_model,
        available_models=llm_status.get('available_models', [])
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
