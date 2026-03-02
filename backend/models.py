"""Pydantic models for API request/response validation."""
from typing import List, Optional
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    """Chat request model."""
    query: str = Field(..., description="User question", min_length=1)
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID")
    doc_type: Optional[str] = Field(None, description="Filter by doc type: 'mysql' or 'python'")

class Source(BaseModel):
    """Source document model."""
    source: str = Field(..., description="Source filename")
    page: int = Field(..., description="Page number")
    content_preview: Optional[str] = Field(None, description="Preview of content")
    doc_type: Optional[str] = Field(None, description="Document type")

class ChatResponse(BaseModel):
    """Chat response model."""
    answer: str = Field(..., description="Generated answer")
    sources: List[Source] = Field(default_factory=list, description="Source documents")
    success: bool = Field(..., description="Whether query was successful")
    error: Optional[str] = Field(None, description="Error message if failed")
    filter_applied: Optional[str] = Field(None, description="Document filter applied")

class DocumentStats(BaseModel):
    """Document statistics model."""
    total_documents: int = Field(..., description="Total number of document chunks")
    persist_directory: str = Field(..., description="Vector store directory")
    embedding_model: str = Field(..., description="Embedding model name")

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Service status")
    ollama_running: bool = Field(..., description="Whether Ollama is running")
    model_available: bool = Field(..., description="Whether model is available")
    vectorstore_initialized: bool = Field(..., description="Whether vectorstore is ready")
    configured_model: str = Field(..., description="Configured Ollama model")
    available_models: List[str] = Field(default_factory=list, description="Available models")

class InitializeResponse(BaseModel):
    """Initialization response model."""
    success: bool = Field(..., description="Whether initialization succeeded")
    message: str = Field(..., description="Status message")
    documents_processed: Optional[int] = Field(None, description="Number of documents processed")
    error: Optional[str] = Field(None, description="Error message if failed")
