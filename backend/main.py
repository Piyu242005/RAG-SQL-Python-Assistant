"""Main FastAPI application."""
import asyncio
import json
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
import os
import httpx
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from models import HealthResponse, InitializeResponse, DocumentStats
from typing import Tuple, List
from llm_config import OllamaManager
from vector_store import VectorStoreManager
from document_processor import DocumentProcessor
from routers import chat
from config import settings
import logging
import time
from pythonjsonlogger import jsonlogger
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from limiter import limiter
from fastapi.responses import JSONResponse
import fitz  # PyMuPDF

# Setup Logging
log_handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
log_handler.setFormatter(formatter)
logger = logging.getLogger("rag-api")
logger.addHandler(log_handler)
logger.setLevel(logging.INFO)

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    print("=" * 60)
    print("[*] Starting RAG System API")
    print("=" * 60)
    
    # Validate Ollama setup
    ollama_manager = OllamaManager()
    status = ollama_manager.validate_setup()
    
    if not status['ollama_running']:
        print("[!] WARNING: Ollama is not running!")
        print("   Please start Ollama: ollama serve")
    elif not status['model_available']:
        print(f"[!] WARNING: Model '{settings.ollama_model}' not found!")
        print(f"   Please pull the model: ollama pull {settings.ollama_model}")
    else:
        print("[OK] Ollama setup validated")
    
    # Check vector store without forcing retriever/bootstrap
    vector_manager = VectorStoreManager()
    stats = vector_manager.get_stats()
    if "error" in stats:
        print(f"[!] WARNING: Vector store check failed: {stats['error']}")
    else:
        print(f"[OK] Vector store found ({stats['total_documents']} documents)")
        # Pre-warm BM25 now so the first real request never triggers a cold rebuild
        print("[*] Pre-warming BM25 cache...")
        vector_manager.initialize_vectorstore()  # ensure vectorstore is loaded
        ok = vector_manager.warm_bm25_cache(k=8)
        if ok:
            print("[OK] BM25 cache ready")
        else:
            print("[!] WARNING: BM25 warm-up failed — first request may be slow")
        
        # Check cache version
        from redis_manager import redis_manager
        version = redis_manager.get_cache_version()
        print(f"[OK] Redis Cache Version: {version}")
    
    print("=" * 60)
    print(f"[*] API running on http://{settings.api_host}:{settings.api_port}")
    print("=" * 60)
    
    yield
    
    # Shutdown
    print("\n[*] Shutting down RAG System API")

# Create FastAPI app
app = FastAPI(
    title="RAG System API",
    description="Retrieval-Augmented Generation system for SQL and Python documentation",
    version="1.0.0",
    lifespan=lifespan
)

# Rate Limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key Middleware
@app.middleware("http")
async def api_key_auth(request: Request, call_next):
    # Only protect /api/chat and /api/initialize, etc.
    # Root and Health can be public
    if request.url.path.startswith("/api") and not request.url.path.endswith("/health"):
        if not settings.api_key:
            return JSONResponse(
                status_code=503,
                content={"error": "Server misconfigured: API_KEY is not set"}
            )
        key = request.headers.get("x-api-key")
        if key != settings.api_key:
            return JSONResponse(
                status_code=401,
                content={"error": "Unauthorized: Invalid or missing API Key"}
            )
    
    response = await call_next(request)
    return response

# Global Error Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.post("/api/reindex")
@limiter.limit("2/hour")
async def reindex(request: Request):
    """Trigger a full vector DB rebuild in a background thread (non-blocking)."""
    from initialize_db import run_pipeline

    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: run_pipeline(force=True, use_semantic=False))
        
        # Increment cache version to invalidate old hits
        from redis_manager import redis_manager
        new_version = redis_manager.increment_cache_version()
        
        logger.info(json.dumps({"action": "reindex_complete", "new_version": new_version}))
        return {"status": "reindexed", "version": new_version}
    except Exception as e:
        logger.error(f"Failed to reindex: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Root endpoint

# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(
        "Request processed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration": f"{duration:.4f}s",
            "client_ip": request.client.host
        }
    )
    return response

# Include routers
app.include_router(chat.router)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Piyu's RAG AI Assistant 🚀",
        "description": "Ask anything about SQL or Python and get accurate answers with page-level citations.",
        "version": "1.0.0",
        "docs": "/docs",
        "author": "Piyush Ramteke",
        "status": "Running successfully"
    }

@app.get("/api/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Check system health and status with absolute path verification."""
    ollama_manager = OllamaManager()
    vector_manager = VectorStoreManager()
    
    status = ollama_manager.validate_setup()
    
    # Verify vectorstore using absolute path stats
    stats = vector_manager.get_stats()
    vectorstore_initialized = "error" not in stats and stats.get('total_documents', 0) > 0
    
    # We consider it healthy if core RAG is working (Ollama + Vector Store)
    is_healthy = status['ollama_running'] and vectorstore_initialized
    
    return HealthResponse(
        status="healthy" if is_healthy else "degraded",
        ollama_running=status['ollama_running'],
        model_available=status['model_available'],
        vectorstore_initialized=vectorstore_initialized,
        configured_model=status['configured_model'],
        available_models=status['available_models']
    )



async def _fetch_ollama_tags() -> tuple[bool, list]:
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"{settings.ollama_base_url}/api/tags")
        if response.status_code != 200:
            return False, []
        payload = response.json()
        models = payload.get("models", []) if isinstance(payload, dict) else []
        return True, models
    except Exception:
        return False, []


@app.get("/api/ready")
async def readiness_check():
    """Readiness endpoint: true only when RAG dependencies are usable."""
    vector_manager = VectorStoreManager()
    stats = vector_manager.get_stats()
    vector_count = stats.get("total_documents", 0)

    ollama_running, models = await _fetch_ollama_tags()
    configured_model = settings.ollama_model
    model_available = any(
        configured_model in model.get("name", "") or model.get("name", "").startswith(configured_model)
        for model in models
        if isinstance(model, dict)
    )

    reasons = []
    if not ollama_running:
        reasons.append("OLLAMA_UNREACHABLE")
    if ollama_running and not model_available:
        reasons.append("MODEL_NOT_LOADED")
    if "error" in stats:
        reasons.append("VECTORSTORE_ERROR")
    elif vector_count <= 0:
        reasons.append("VECTORSTORE_EMPTY")

    ready = ollama_running and model_available and vector_count > 0 and "error" not in stats

    return {
        "ready": ready,
        "ollama_running": ollama_running,
        "model_available": model_available,
        "vectorstore_docs": vector_count,
        "reasons": reasons,
        "vectorstore_error": stats.get("error"),
    }

@app.post("/api/initialize", response_model=InitializeResponse)
async def initialize_system() -> InitializeResponse:
    """
    Initialize or reinitialize the RAG system.
    Process PDFs and create vector store.
    
    Returns:
        InitializeResponse with initialization status
    """
    try:
        print("\n[*] Starting system initialization...")
        
        # Process documents
        processor = DocumentProcessor()
        documents = processor.process_all_pdfs()
        
        if not documents:
            return InitializeResponse(
                success=False,
                message="No documents processed",
                error="No PDF files found or failed to process"
            )
        
        # Initialize vector store
        vector_manager = VectorStoreManager()
        vector_manager.reset_vectorstore()  # Clear existing
        vector_manager.initialize_vectorstore(documents)
        
        return InitializeResponse(
            success=True,
            message="System initialized successfully",
            documents_processed=len(documents)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload", response_model=InitializeResponse)
async def upload_pdf(file: UploadFile = File(...), doc_type: str = "custom") -> InitializeResponse:
    """
    Upload a new PDF and index it into the vector store.
    """
    MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB hard limit

    try:
        # 1. Read with size guard — reject before touching disk
        contents = await file.read(MAX_UPLOAD_BYTES + 1)
        if len(contents) > MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum allowed size is 50 MB."
            )

        # 2. Strict MIME-type and extension validation
        allowed_extensions = {".pdf"}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions or file.content_type != "application/pdf":
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only PDF files are supported."
            )
        
        # 3. Simple magic number check (PDFs start with %PDF)
        if not contents.startswith(b"%PDF"):
            raise HTTPException(
                status_code=400,
                detail="Malformed file. The uploaded file is not a valid PDF."
            )

        # 4. Deep Inspection (Encrypted / Page Count)
        try:
            with fitz.open(stream=contents, filetype="pdf") as doc:
                if doc.is_encrypted:
                    raise HTTPException(
                        status_code=400,
                        detail="Encrypted PDFs are not supported for indexing."
                    )
                if doc.page_count > 500:
                    raise HTTPException(
                        status_code=400,
                        detail=f"File too large. Maximum allowed is 500 pages (found {doc.page_count})."
                    )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"PDF inspection failed: {e}")
            raise HTTPException(status_code=400, detail="Invalid or corrupt PDF document.")

        # 5. Save file safely
        safe_filename = os.path.basename(file.filename)
        file_path = settings.pdf_directory / safe_filename
        with open(file_path, "wb") as buffer:
            buffer.write(contents)

        # 3. Process document
        processor = DocumentProcessor()
        documents = processor.process_pdf(file_path, doc_type)

        # 4. Add to vector store
        vector_manager = VectorStoreManager()
        vector_manager.add_documents(documents)

        return InitializeResponse(
            success=True,
            message=f"File '{file.filename}' uploaded and indexed successfully",
            documents_processed=len(documents)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents", response_model=DocumentStats)
async def get_documents_stats() -> DocumentStats:
    """
    Get statistics about indexed documents.
    
    Returns:
        DocumentStats with vector store statistics
    """
    vector_manager = VectorStoreManager()
    stats = vector_manager.get_stats()
    
    if "error" in stats:
        return DocumentStats(
            total_documents=0,
            persist_directory=settings.chroma_persist_directory,
            embedding_model=settings.embedding_model
        )
    
    return DocumentStats(**stats)

# Run with: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
