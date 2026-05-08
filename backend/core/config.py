"""Configuration management for the RAG system."""
import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings."""
    
    # Project Info
    project_name: str = "Piyu's RAG Assistant"
    version: str = "2.0.0"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Feature Flags
    enable_hyde: bool = os.getenv("ENABLE_HYDE", "false").lower() == "true"
    enable_reranker: bool = os.getenv("ENABLE_RERANKER", "true").lower() == "true"
    enable_cache: bool = os.getenv("ENABLE_CACHE", "true").lower() == "true"
    enable_summarization: bool = os.getenv("ENABLE_SUMMARIZATION", "false").lower() == "true"
    
    # LLM Provider Configuration
    llm_provider: str = os.getenv("LLM_PROVIDER", "ollama") # ollama, openai, claude
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.2")
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Embedding Model
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    
    # Paths
    base_dir: Path = Path(__file__).resolve().parent.parent.parent
    data_dir: Path = base_dir / "data"
    pdf_directory: Path = data_dir / "pdfs"
    media_directory: Path = data_dir / "media"
    chroma_persist_directory: str = os.getenv("CHROMA_PERSIST_DIRECTORY", str(data_dir / "chroma_db"))
    
    # Redis Configuration
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_cache_ttl_sec: int = int(os.getenv("REDIS_CACHE_TTL_SEC", "86400"))
    
    # Document Processing
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "600"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "100"))
    
    # RAG Context limits
    max_context_tokens: int = int(os.getenv("MAX_CONTEXT_TOKENS", "3000"))
    max_history_messages: int = int(os.getenv("MAX_HISTORY_MESSAGES", "6"))
    
    # Timeouts & Circuit Breakers
    query_expansion_timeout_sec: float = float(os.getenv("QUERY_EXPANSION_TIMEOUT_SEC", "3.0"))
    reranker_timeout_sec: float = float(os.getenv("RERANKER_TIMEOUT_SEC", "2.0"))
    llm_timeout_sec: float = float(os.getenv("LLM_TIMEOUT_SEC", "30.0"))
    
    # API Configuration
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    api_key: str = os.getenv("API_KEY", "")
    
    # CORS
    cors_origins: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,http://localhost:8501").split(",")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def normalize_cors_origins(cls, value):
        if isinstance(value, str):
            return [v.strip() for v in value.split(",") if v.strip()]
        return value
    
    enable_query_expansion: bool = os.getenv("ENABLE_QUERY_EXPANSION", "false").lower() == "true"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

# Create settings instance
settings = Settings()
