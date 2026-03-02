"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from models import HealthResponse, InitializeResponse, DocumentStats
from llm_config import OllamaManager
from vector_store import VectorStoreManager
from document_processor import DocumentProcessor
from routers import chat
from config import settings

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
    
    # Check vector store
    vector_manager = VectorStoreManager()
    if vector_manager._vectorstore_exists():
        print("[OK] Vector store found")
    else:
        print("[!] WARNING: Vector store not initialized!")
        print("   Please run: python initialize_db.py")
    
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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "RAG System API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/api/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Check system health and status.
    
    Returns:
        HealthResponse with system status
    """
    ollama_manager = OllamaManager()
    vector_manager = VectorStoreManager()
    
    status = ollama_manager.validate_setup()
    vectorstore_exists = vector_manager._vectorstore_exists()
    
    return HealthResponse(
        status="healthy" if status['ollama_running'] and vectorstore_exists else "degraded",
        ollama_running=status['ollama_running'],
        model_available=status['model_available'],
        vectorstore_initialized=vectorstore_exists,
        configured_model=status['configured_model'],
        available_models=status['available_models']
    )

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
        return InitializeResponse(
            success=False,
            message="Initialization failed",
            error=str(e)
        )

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
