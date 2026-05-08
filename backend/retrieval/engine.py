import logging
import pickle
from pathlib import Path
from typing import List, Optional
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from core.config import settings
from storage.vector import VectorStorage

try:
    from langchain.retrievers import EnsembleRetriever
except ImportError:
    try:
        from langchain_classic.retrievers import EnsembleRetriever
    except ImportError:
        from langchain_community.retrievers.ensemble import EnsembleRetriever

logger = logging.getLogger("retrieval-engine")

class RetrievalEngine:
    """Handles high-level retrieval logic (Hybrid, BM25, Vector)."""
    
    def __init__(self, vector_storage: VectorStorage):
        self.storage = vector_storage
        self._bm25_retriever = None

    def get_hybrid_retriever(self, k: int = 4, vector_weight: float = 0.7, bm25_weight: float = 0.3):
        vs = self.storage.get_vectorstore()
        
        # BM25 logic
        cache_path = Path(self.storage.persist_directory) / "bm25_retriever.pkl"
        bm25 = self._load_or_rebuild_bm25(k, cache_path)
        
        if hasattr(bm25, 'k'):
            bm25.k = k

        vector = vs.as_retriever(search_kwargs={"k": k})

        return EnsembleRetriever(
            retrievers=[vector, bm25],
            weights=[vector_weight, bm25_weight]
        )

    def _load_or_rebuild_bm25(self, k: int, cache_path: Path) -> BM25Retriever:
        if self._bm25_retriever:
            return self._bm25_retriever
            
        if cache_path.exists():
            try:
                with open(cache_path, "rb") as f:
                    self._bm25_retriever = pickle.load(f)
                    return self._bm25_retriever
            except Exception as e:
                logger.warning(f"BM25 cache corrupt, rebuilding: {e}")
        
        return self._rebuild_bm25(k, cache_path)

    def _rebuild_bm25(self, k: int, path: Path) -> BM25Retriever:
        logger.info("Rebuilding BM25 index...")
        vs = self.storage.get_vectorstore()
        results = vs.get()
        
        docs = [
            Document(page_content=results['documents'][i], metadata=results['metadatas'][i])
            for i in range(len(results['ids']))
        ]
        
        if not docs:
            # Fallback to empty retriever or similar
            return BM25Retriever.from_documents([Document(page_content="initial")])

        bm25 = BM25Retriever.from_documents(docs)
        with open(path, "wb") as f:
            pickle.dump(bm25, f)
        
        self._bm25_retriever = bm25
        return bm25
