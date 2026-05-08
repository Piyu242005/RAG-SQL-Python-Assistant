from typing import Generator
from core.config import settings
from providers.factory import LLMFactory
from storage.vector import VectorStorage
from retrieval.engine import RetrievalEngine
from cache.redis import RedisCache
from memory.session import SessionMemory
from services.chat import ChatService
from services.document import DocumentService

# Shared instances (Singleton-like behavior for some)
_storage = VectorStorage()
_cache = RedisCache()
_memory = SessionMemory(redis_url=settings.redis_url)
_retrieval = RetrievalEngine(_storage)

def get_llm():
    return LLMFactory.get_provider()

def get_chat_service():
    return ChatService(
        llm=get_llm(),
        retrieval=_retrieval,
        cache=_cache,
        memory=_memory
    )

def get_document_service():
    return DocumentService(
        storage=_storage,
        cache=_cache
    )
