import logging
from typing import List, Optional
from pathlib import Path
from storage.vector import VectorStorage
from cache.redis import RedisCache
from core.config import settings

logger = logging.getLogger("document-service")

class DocumentService:
    """Handles document indexing and management."""
    
    def __init__(self, storage: VectorStorage, cache: RedisCache):
        self.storage = storage
        self.cache = cache

    def index_documents(self, documents: List[Any]):
        """Index documents into the vector store."""
        logger.info(f"Indexing {len(documents)} documents...")
        self.storage.add_documents(documents)
        
        # Invalidate cache by incrementing version
        new_version = self.cache.increment_version()
        logger.info(f"Cache version incremented to {new_version}")

    def reindex_all(self):
        """Full reindex of all documents in the PDF directory."""
        # This will be expanded in Phase 4 with Celery
        pass

    def get_stats(self) -> dict:
        return self.storage.get_stats()

    def reset_system(self):
        self.storage.reset()
        self.cache.increment_version()
