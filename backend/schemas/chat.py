from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ChatRequest(BaseModel):
    """Request schema for chat endpoints."""
    query: str = Field(..., description="The user's question")
    conversation_id: Optional[str] = Field("default", description="Session ID for history tracking")
    doc_type: Optional[str] = Field(None, description="Optional document type filter")

class SourceMetadata(BaseModel):
    """Metadata for a source document."""
    source: str
    page: str
    content_preview: Optional[str] = None

class ChatResponse(BaseModel):
    """Response schema for synchronous chat."""
    answer: str
    sources: List[SourceMetadata]
    success: bool = True

class StreamChunk(BaseModel):
    """Schema for a single chunk in a stream."""
    token: Optional[str] = None
    sources: Optional[List[SourceMetadata]] = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    """System health status response."""
    status: str
    ollama_running: bool
    model_available: bool
    vectorstore_initialized: bool
    configured_model: str
    available_models: List[str]

class InitializeResponse(BaseModel):
    """Response schema for initialization."""
    success: bool
    message: str
    documents_processed: Optional[int] = None
    error: Optional[str] = None

class DocumentStats(BaseModel):
    """Statistics about indexed documents."""
    total_documents: int
    persist_directory: str
    embedding_model: str
