"""Document processing module for extracting and chunking PDF content."""
import os
from pathlib import Path
from typing import List, Dict
import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from config import settings

class DocumentProcessor:
    """Process PDF documents for RAG system."""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        """Initialize document processor.
        
        Args:
            chunk_size: Size of text chunks (defaults to settings)
            chunk_overlap: Overlap between chunks (defaults to settings)
        """
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        
        # Initialize text splitter with semantic chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],  # Preserve paragraphs and sentences
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
    
    def chunk_documents(self, pages_data: List[Dict[str, any]], doc_type: str) -> List[Document]:
        """Split pages into chunks and create LangChain Document objects.
        
        Args:
            pages_data: List of page data dictionaries
            doc_type: Type of document ('mysql' or 'python')
            
        Returns:
            List of LangChain Document objects
        """
        documents = []
        
        for page_data in pages_data:
            # Split page text into chunks
            chunks = self.text_splitter.split_text(page_data["text"])
            
            for i, chunk in enumerate(chunks):
                # Create Document with metadata
                doc = Document(
                    page_content=chunk,
                    metadata={
                        "source": page_data["source"],
                        "page": page_data["page_number"],
                        "chunk": i,
                        "doc_type": doc_type
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
    
    def process_all_pdfs(self) -> List[Document]:
        """Process all PDF files in the workspace.
        
        Returns:
            List of all processed Document objects
        """
        print("=" * 60)
        print(" Starting PDF Processing")
        print("=" * 60)
        
        all_documents = []
        
        # Define PDFs to process with their types
        pdf_configs = [
            {"filename": "MySQL Handbook.pdf", "doc_type": "mysql"},
            {"filename": "The Ultimate Python Handbook.pdf", "doc_type": "python"}
        ]
        
        for config in pdf_configs:
            pdf_path = settings.pdf_directory / config["filename"]
            
            if not pdf_path.exists():
                print(f"[!]  Warning: {config['filename']} not found at {pdf_path}")
                continue
            
            try:
                documents = self.process_pdf(pdf_path, config["doc_type"])
                all_documents.extend(documents)
            except Exception as e:
                print(f"[X] Failed to process {config['filename']}: {str(e)}")
        
        print("\n" + "=" * 60)
        print(f"[OK] Processing Complete: {len(all_documents)} total chunks")
        print("=" * 60)
        
        return all_documents


# Example usage
if __name__ == "__main__":
    processor = DocumentProcessor()
    documents = processor.process_all_pdfs()
    print(f"\nProcessed {len(documents)} document chunks")
    
    # Show sample
    if documents:
        print("\nSample chunk:")
        print(f"Content: {documents[0].page_content[:200]}...")
        print(f"Metadata: {documents[0].metadata}")
