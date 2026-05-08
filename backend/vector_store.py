"""Backward compatibility adapter for VectorStoreManager."""
from pathlib import Path
from storage.vector import VectorStorage
from retrieval.engine import RetrievalEngine
from core.config import settings

_storage = VectorStorage()
_engine = RetrievalEngine(_storage)

class VectorStoreManager:
    def __init__(self):
        self.persist_directory = _storage.persist_directory
        self.embedding_model_name = _storage.embedding_model_name
        self.embeddings = _storage.embeddings
        self.vectorstore = _storage.vectorstore

    def initialize_vectorstore(self, documents=None):
        return _storage.get_vectorstore(documents)

    def add_documents(self, documents):
        _storage.add_documents(documents)

    def similarity_search(self, query, k=4, filter=None):
        vs = _storage.get_vectorstore()
        return vs.similarity_search(query, k=k, filter=filter)

    def similarity_search_with_score(self, query, k=4, filter=None):
        vs = _storage.get_vectorstore()
        return vs.similarity_search_with_score(query, k=k, filter=filter)

    def get_retriever(self, k=4, search_type="mmr"):
        vs = _storage.get_vectorstore()
        return vs.as_retriever(search_type=search_type, search_kwargs={"k": k})

    def get_hybrid_retriever(self, k=4, vector_weight=0.7, bm25_weight=0.3):
        return _engine.get_hybrid_retriever(k, vector_weight, bm25_weight)

    def warm_bm25_cache(self, k=8):
        # engine handles this lazily or we can call it here
        _engine._load_or_rebuild_bm25(k, Path(_storage.persist_directory) / "bm25_retriever.pkl")
        return True

    def get_stats(self):
        stats = _storage.get_stats()
        stats.update({
            "persist_directory": self.persist_directory,
            "embedding_model": self.embedding_model_name
        })
        return stats

    def reset_vectorstore(self):
        _storage.reset()
