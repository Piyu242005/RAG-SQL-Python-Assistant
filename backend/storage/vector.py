import logging
import chromadb
from pathlib import Path
from typing import List, Optional, Any
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from core.config import settings

logger = logging.getLogger("vector-storage")

class VectorStorage:
    """Handles low-level vector database operations."""
    
    def __init__(self):
        self.persist_directory = settings.chroma_persist_directory
        self.embedding_model_name = settings.embedding_model
        self.embeddings = None
        self.vectorstore = None
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)

    def _get_embeddings(self) -> HuggingFaceEmbeddings:
        if self.embeddings is None:
            logger.info(f"Loading embedding model: {self.embedding_model_name}")
            self.embeddings = HuggingFaceEmbeddings(
                model_name=self.embedding_model_name,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        return self.embeddings

    def get_vectorstore(self, documents: Optional[List[Document]] = None) -> Chroma:
        embeddings = self._get_embeddings()
        
        if self.vectorstore is not None and documents is None:
            return self.vectorstore

        db_exists = (Path(self.persist_directory) / "chroma.sqlite3").exists()
        
        if db_exists and documents is None:
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=embeddings,
                collection_name="rag_documents"
            )
        else:
            if documents:
                self.vectorstore = Chroma.from_documents(
                    documents=documents,
                    embedding=embeddings,
                    persist_directory=self.persist_directory,
                    collection_name="rag_documents"
                )
            else:
                self.vectorstore = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=embeddings,
                    collection_name="rag_documents"
                )
        return self.vectorstore

    def add_documents(self, documents: List[Document]):
        vs = self.get_vectorstore()
        vs.add_documents(documents)
        # Handle BM25 invalidation via signals or orchestrator

    def get_stats(self) -> dict:
        try:
            db_path = Path(self.persist_directory)
            if not db_path.exists() or not (db_path / "chroma.sqlite3").exists():
                return {"total_documents": 0}
            
            client = chromadb.PersistentClient(path=str(db_path))
            collection = client.get_or_create_collection(name="rag_documents")
            return {"total_documents": collection.count()}
        except Exception as e:
            logger.error(f"Failed to get vector stats: {e}")
            return {"error": str(e), "total_documents": 0}

    def reset(self):
        import shutil
        if Path(self.persist_directory).exists():
            shutil.rmtree(self.persist_directory)
        self.vectorstore = None
