"""Document processing module for extracting and chunking PDF content."""
import os
from pathlib import Path
from typing import List, Dict
import fitz  # PyMuPDF
from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from config import settings

class DocumentProcessor:
    """Process PDF documents for RAG system."""
    
    def __init__(self, use_semantic: bool = False):
        """Initialize document processor.
        
        Args:
            use_semantic: Whether to use computationally expensive SemanticChunker.
                          Defaults to False for better performance during bulk indexing.
        """
        self.embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model)
        self.use_semantic = use_semantic
        
        if self.use_semantic:
            # High-precision but slow
            self.text_splitter = SemanticChunker(
                self.embeddings,
                breakpoint_threshold_type="percentile"
            )
        else:
            # Fast and reliable (Optimized Recursive Splitter)
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.chunk_size,
                chunk_overlap=settings.chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", ". ", " ", ""],
                keep_separator=True
            )
    
    def extract_text_from_pdf(self, pdf_path: Path) -> List[Dict[str, any]]:
        """Extract text from PDF with metadata.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of dictionaries containing text and metadata for each page
        """
        pages_data = []
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                
                # Skip empty pages
                if text.strip():
                    pages_data.append({
                        "text": text,
                        "page_number": page_num + 1,  # 1-indexed for user display
                        "source": pdf_path.name
                    })
            
            doc.close()
            print(f"[OK] Extracted {len(pages_data)} pages from {pdf_path.name}")
            
        except Exception as e:
            print(f"[X] Error extracting text from {pdf_path.name}: {str(e)}")
            raise
        
        return pages_data
    
    def _detect_topic(self, text: str) -> str:
        """Detect the primary topic of a chunk for metadata filtering."""
        text = text.lower()
        
        # SQL Heuristics
        sql_keywords = ['join', 'select', 'where', 'group by', 'insert', 'update', 'delete', 'table', 'database']
        # Python Heuristics
        python_keywords = ['def ', 'class ', 'import ', 'decorators', 'list comprehension', 'try:', 'except:', 'async', 'await']
        
        if any(k in text for k in sql_keywords):
            if 'join' in text: return "sql_joins"
            if 'select' in text: return "sql_queries"
            return "sql_general"
        
        if any(k in text for k in python_keywords):
            if 'decorator' in text: return "python_decorators"
            if 'class' in text: return "python_oop"
            return "python_general"
            
        return "general_tech"

    def chunk_documents(self, pages_data: List[Dict[str, any]], doc_type: str) -> List[Document]:
        """Split pages into chunks and create LangChain Document objects with topic tagging."""
        documents = []
        
        for page_data in pages_data:
            # Split page text into chunks
            chunks = self.text_splitter.split_text(page_data["text"])
            
            for i, chunk in enumerate(chunks):
                # Detect topic for this specific chunk
                topic = self._detect_topic(chunk)
                
                # Create Document with metadata
                doc = Document(
                    page_content=chunk,
                    metadata={
                        "source": page_data["source"],
                        "page": page_data["page_number"],
                        "chunk": i,
                        "doc_type": doc_type,
                        "topic": topic  # NEW: Topic tagging
                    }
                )
                documents.append(doc)
        
        return documents
    
    def process_pdf(self, pdf_path: Path, doc_type: str) -> List[Document]:
        """Process a single PDF file.
        
        Args:
            pdf_path: Path to PDF file
            doc_type: Type of document ('mysql' or 'python')
            
        Returns:
            List of processed Document objects
        """
        print(f"\n Processing {pdf_path.name}...")
        
        # Extract text from PDF
        pages_data = self.extract_text_from_pdf(pdf_path)
        
        # Chunk documents
        documents = self.chunk_documents(pages_data, doc_type)
        
        print(f"[OK] Created {len(documents)} chunks from {pdf_path.name}")
        
        return documents


# Example usage
if __name__ == "__main__":
    processor = DocumentProcessor()
    # The actual processing is usually done via initialize_db.py
    print("DocumentProcessor ready.")
