"""Vector store management using ChromaDB."""
import os
from typing import List, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from config import settings

class VectorStoreManager:
    """Manage ChromaDB vector store for document embeddings."""
    
    def __init__(self):
        """Initialize vector store manager."""
        self.persist_directory = settings.chroma_persist_directory
        self.embedding_model_name = settings.embedding_model
        self.embeddings = None
        self.vectorstore = None
        
        # Create persist directory if it doesn't exist
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
    
    def _initialize_embeddings(self):
        """Initialize HuggingFace embeddings."""
        if self.embeddings is None:
            print(f"🔄 Loading embedding model: {self.embedding_model_name}")
            self.embeddings = HuggingFaceEmbeddings(
                model_name=self.embedding_model_name,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            print("✓ Embedding model loaded")
    
    def initialize_vectorstore(self, documents: Optional[List[Document]] = None) -> Chroma:
        """Initialize or load ChromaDB vector store.
        
        Args:
            documents: Optional list of documents to add to new vector store
            
        Returns:
            Chroma vectorstore instance
        """
        self._initialize_embeddings()
        
        # Check if vectorstore already exists
        if self._vectorstore_exists() and documents is None:
            print("📦 Loading existing vector store...")
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
                collection_name="rag_documents"
            )
            print(f"✓ Loaded vector store from {self.persist_directory}")
        else:
            if documents:
                print(f"🔄 Creating new vector store with {len(documents)} documents...")
                self.vectorstore = Chroma.from_documents(
                    documents=documents,
                    embedding=self.embeddings,
                    persist_directory=self.persist_directory,
                    collection_name="rag_documents"
                )
                print(f"✓ Vector store created and persisted to {self.persist_directory}")
            else:
                # Create empty vectorstore
                print("🔄 Creating empty vector store...")
                self.vectorstore = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings,
                    collection_name="rag_documents"
                )
                print("✓ Empty vector store created")
        
        return self.vectorstore
    
    def _vectorstore_exists(self) -> bool:
        """Check if vector store already exists.
        
        Returns:
            True if vectorstore exists, False otherwise
        """
        chroma_db_path = Path(self.persist_directory) / "chroma.sqlite3"
        return chroma_db_path.exists()
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to existing vector store.
        
        Args:
            documents: List of documents to add
        """
        if self.vectorstore is None:
            self.initialize_vectorstore()
        
        print(f"➕ Adding {len(documents)} documents to vector store...")
        self.vectorstore.add_documents(documents)
        print("✓ Documents added successfully")
    
    def similarity_search(
        self, 
        query: str, 
        k: int = 4,
        filter: Optional[dict] = None
    ) -> List[Document]:
        """Perform similarity search in vector store.
        
        Args:
            query: Search query
            k: Number of results to return
            filter: Optional metadata filter (e.g., {"doc_type": "mysql"})
            
        Returns:
            List of relevant documents
        """
        if self.vectorstore is None:
            self.initialize_vectorstore()
        
        return self.vectorstore.similarity_search(
            query=query,
            k=k,
            filter=filter
        )
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        filter: Optional[dict] = None
    ) -> List[tuple]:
        """Perform similarity search with relevance scores.
        
        Args:
            query: Search query
            k: Number of results to return
            filter: Optional metadata filter
            
        Returns:
            List of tuples (document, score)
        """
        if self.vectorstore is None:
            self.initialize_vectorstore()
        
        return self.vectorstore.similarity_search_with_score(
            query=query,
            k=k,
            filter=filter
        )
    
    def get_retriever(self, k: int = 4, search_type: str = "mmr"):
        """Get a retriever for the vector store.
        
        Args:
            k: Number of documents to retrieve
            search_type: Type of search ('similarity' or 'mmr')
            
        Returns:
            VectorStoreRetriever instance
        """
        if self.vectorstore is None:
            self.initialize_vectorstore()
        
        return self.vectorstore.as_retriever(
            search_type=search_type,
            search_kwargs={"k": k}
        )
    
    def get_stats(self) -> dict:
        """Get statistics about the vector store.
        
        Returns:
            Dictionary with store statistics
        """
        if self.vectorstore is None:
            self.initialize_vectorstore()
        
        try:
            collection = self.vectorstore._collection
            count = collection.count()
            
            return {
                "total_documents": count,
                "persist_directory": self.persist_directory,
                "embedding_model": self.embedding_model_name
            }
        except Exception as e:
            return {"error": str(e)}
    
    def reset_vectorstore(self) -> None:
        """Delete and reset the vector store."""
        import shutil
        
        if Path(self.persist_directory).exists():
            shutil.rmtree(self.persist_directory)
            print(f"✓ Vector store deleted: {self.persist_directory}")
        
        self.vectorstore = None
        print("✓ Vector store reset complete")


# Example usage
if __name__ == "__main__":
    manager = VectorStoreManager()
    
    # Check if vectorstore exists
    if manager._vectorstore_exists():
        manager.initialize_vectorstore()
        stats = manager.get_stats()
        print(f"\nVector Store Stats: {stats}")
    else:
        print("No existing vector store found. Run initialize_db.py first.")
