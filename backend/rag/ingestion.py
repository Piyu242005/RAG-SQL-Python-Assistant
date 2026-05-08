from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from storage.vector_store import VectorStore
import logging

class IngestionPipeline:
    def __init__(self):
        self.vector_store = VectorStore()
        # Optimized for code and text
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", "", "def ", "class ", "import ", "SELECT ", "CREATE "]
        )

    async def process(self, file_path: str):
        try:
            logging.info(f"Starting ingestion for: {file_path}")
            
            # 1. Load PDF
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            
            # 2. Split into chunks
            chunks = self.splitter.split_documents(docs)
            
            # 3. Add to vector store
            self.vector_store.add_documents(chunks)
            
            logging.info(f"Successfully indexed {len(chunks)} chunks from {file_path}")
            return len(chunks)
        except Exception as e:
            logging.error(f"Failed to ingest document: {str(e)}")
            raise
