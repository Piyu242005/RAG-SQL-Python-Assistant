"""Vector store management using ChromaDB."""
import os
from typing import List, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever

try:
    from langchain.retrievers import EnsembleRetriever
except ImportError:
    try:
        from langchain_classic.retrievers import EnsembleRetriever
    except ImportError:
        from langchain_community.retrievers.ensemble import EnsembleRetriever

from config import settings


class VectorStoreManager:
    """Manage ChromaDB vector store for document embeddings."""

    def __init__(self):
        self.persist_directory = settings.chroma_persist_directory
        self.embedding_model_name = settings.embedding_model
        self.embeddings = None
        self.vectorstore = None

        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)

    # ───────────────────────────────────────────────
    # Embeddings
    # ───────────────────────────────────────────────
    def _initialize_embeddings(self):
        if self.embeddings is None:
            print(f" Loading embedding model: {self.embedding_model_name}")
            self.embeddings = HuggingFaceEmbeddings(
                model_name=self.embedding_model_name,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            print("[OK] Embedding model loaded")

    # ───────────────────────────────────────────────
    # Vector Store Init
    # ───────────────────────────────────────────────
    def initialize_vectorstore(self, documents: Optional[List[Document]] = None) -> Chroma:
        self._initialize_embeddings()

        if self._vectorstore_exists() and documents is None:
            print(" Loading existing vector store...")
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
                collection_name="rag_documents"
            )
        else:
            if documents:
                print(f" Creating vector store with {len(documents)} docs...")
                self.vectorstore = Chroma.from_documents(
                    documents=documents,
                    embedding=self.embeddings,
                    persist_directory=self.persist_directory,
                    collection_name="rag_documents"
                )
            else:
                print(" Creating empty vector store...")
                self.vectorstore = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings,
                    collection_name="rag_documents"
                )

        return self.vectorstore

    def _vectorstore_exists(self) -> bool:
        return (Path(self.persist_directory) / "chroma.sqlite3").exists()

    # ───────────────────────────────────────────────
    # Add Documents
    # ───────────────────────────────────────────────
    def add_documents(self, documents: List[Document]) -> None:
        if self.vectorstore is None:
            self.initialize_vectorstore()

        print(f" Adding {len(documents)} documents...")
        self.vectorstore.add_documents(documents)

        # Clear BM25 cache
        bm25_cache_path = Path(self.persist_directory) / "bm25_retriever.pkl"
        if bm25_cache_path.exists():
            bm25_cache_path.unlink()

        if hasattr(self, '_bm25_retriever'):
            self._bm25_retriever = None

    # ───────────────────────────────────────────────
    # Search
    # ───────────────────────────────────────────────
    def similarity_search(self, query: str, k: int = 4, filter: Optional[dict] = None):
        if self.vectorstore is None:
            self.initialize_vectorstore()

        return self.vectorstore.similarity_search(query=query, k=k, filter=filter)

    def similarity_search_with_score(self, query: str, k: int = 4, filter=None):
        if self.vectorstore is None:
            self.initialize_vectorstore()

        return self.vectorstore.similarity_search_with_score(query, k=k, filter=filter)

    # ───────────────────────────────────────────────
    # Retriever
    # ───────────────────────────────────────────────
    def get_retriever(self, k=4, search_type="mmr"):
        if self.vectorstore is None:
            self.initialize_vectorstore()

        return self.vectorstore.as_retriever(
            search_type=search_type,
            search_kwargs={"k": k}
        )

    # ───────────────────────────────────────────────
    # Hybrid Retriever
    # ───────────────────────────────────────────────
    def get_hybrid_retriever(self, k=4, vector_weight=0.7, bm25_weight=0.3):
        if self.vectorstore is None:
            self.initialize_vectorstore()

        import pickle
        cache_path = Path(self.persist_directory) / "bm25_retriever.pkl"

        if hasattr(self, '_bm25_retriever') and self._bm25_retriever:
            bm25 = self._bm25_retriever

        elif cache_path.exists():
            try:
                with open(cache_path, "rb") as f:
                    bm25 = pickle.load(f)
                self._bm25_retriever = bm25
            except:
                bm25 = self._rebuild_bm25(k, cache_path)

        else:
            bm25 = self._rebuild_bm25(k, cache_path)

        if hasattr(bm25, 'k'):
            bm25.k = k

        vector = self.vectorstore.as_retriever(search_kwargs={"k": k})

        return EnsembleRetriever(
            retrievers=[vector, bm25],
            weights=[vector_weight, bm25_weight]
        )

    def _rebuild_bm25(self, k, path):
        print(" Rebuilding BM25 index...")
        import pickle

        results = self.vectorstore.get()
        docs = []

        for i in range(len(results['ids'])):
            docs.append(Document(
                page_content=results['documents'][i],
                metadata=results['metadatas'][i]
            ))

        if not docs:
            return self.get_retriever(k=k)

        bm25 = BM25Retriever.from_documents(docs)

        with open(path, "wb") as f:
            pickle.dump(bm25, f)

        self._bm25_retriever = bm25
        return bm25

    # ───────────────────────────────────────────────
    # Stats (FIXED)
    # ───────────────────────────────────────────────
    def get_stats(self) -> dict:
        """Safe stats (no embedding dependency)."""
        try:
            db_path = Path(self.persist_directory)

            if not db_path.exists() or not (db_path / "chroma.sqlite3").exists():
                return {
                    "total_documents": 0,
                    "persist_directory": self.persist_directory,
                    "embedding_model": self.embedding_model_name,
                }

            client = chromadb.PersistentClient(path=str(db_path))
            collection = client.get_or_create_collection(name="rag_documents")

            return {
                "total_documents": collection.count(),
                "persist_directory": self.persist_directory,
                "embedding_model": self.embedding_model_name,
            }

        except Exception as e:
            return {
                "error": str(e),
                "total_documents": 0,
                "persist_directory": self.persist_directory,
                "embedding_model": self.embedding_model_name,
            }

    # ───────────────────────────────────────────────
    # Reset
    # ───────────────────────────────────────────────
    def reset_vectorstore(self):
        import shutil

        if Path(self.persist_directory).exists():
            shutil.rmtree(self.persist_directory)

        self.vectorstore = None