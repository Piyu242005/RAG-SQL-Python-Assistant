from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os

class VectorStore:
    def __init__(self):
        # Using a reliable embedding model
        self.embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en-v1.5",
            model_kwargs={'device': 'cpu'} # Change to 'cuda' if GPU available
        )
        
        persist_directory = "./chroma_db"
        
        self.db = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings,
            collection_name="enterprise_rag"
        )

    def add_documents(self, documents):
        self.db.add_documents(documents)

    def search(self, query: str, k: int = 5):
        return self.db.similarity_search(query, k=k)
