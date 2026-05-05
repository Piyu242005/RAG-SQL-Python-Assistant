"""Configuration management for the RAG system."""
import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings."""
    
    # Ollama Configuration
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.2")
    
    # Embedding Model
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    
    # Paths
    base_dir: Path = Path(__file__).resolve().parent.parent
    pdf_directory: Path = base_dir / "data" / "pdfs"
    media_directory: Path = base_dir / "data" / "media"
    
    # Vector Store
    chroma_persist_directory: str = os.getenv("CHROMA_PERSIST_DIRECTORY", str(base_dir / "data" / "chroma_db"))
    
    # Redis Configuration
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Document Processing
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "600"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "100"))

    # Feature Flags
    enable_query_expansion: bool = os.getenv("ENABLE_QUERY_EXPANSION", "false").lower() == "true"
    
    # RAG Context limits
    max_context_tokens: int = int(os.getenv("MAX_CONTEXT_TOKENS", "3000"))
    max_history_messages: int = int(os.getenv("MAX_HISTORY_MESSAGES", "6"))
    
    # API Configuration
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    
    # Security
    api_key: str = os.getenv("API_KEY", "")
    
    # CORS
    cors_origins: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def normalize_cors_origins(cls, value):
        if isinstance(value, str):
            return [v.strip() for v in value.split(",") if v.strip()]
        return value
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create settings instance
settings = Settings()
