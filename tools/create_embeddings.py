"""
Standalone Embedding Generator for Piyu RAG
Processes PDFs -> Chunks -> HuggingFace Embeddings -> ChromaDB
"""

import os
import sys
import time
from pathlib import Path
from typing import List, Optional

# Core RAG Dependencies
import fitz  # PyMuPDF
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Add backend to path so we can import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from config import settings

# Configuration (Synced with central settings)
PDF_DIR = settings.pdf_directory
CHROMA_DIR = Path(settings.chroma_persist_directory)
EMBEDDING_MODEL = settings.embedding_model
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
COLLECTION_NAME = "rag_documents"

def check_db_exists() -> bool:
    """Checks if the vector database already exists on disk."""
    db_file = CHROMA_DIR / "chroma.sqlite3"
    return db_file.exists()

def load_pdfs() -> List[dict]:
    """Scans pdfs/ directory and extracts text from all PDFs."""
    if not PDF_DIR.exists():
        print(f"Error: Directory '{PDF_DIR}' not found.")
        return []

    pdf_files = list(PDF_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"Warning: No PDF files found in '{PDF_DIR}'.")
        return []

    print(f"Found {len(pdf_files)} PDF(s). Extracting text...")
    all_pages = []

    for pdf_path in pdf_files:
        try:
            doc = fitz.open(pdf_path)
            for page_num, page in enumerate(doc):
                text = page.get_text().strip()
                if text:
                    all_pages.append({
                        "text": text,
                        "source": pdf_path.name,
                        "page": page_num + 1
                    })
            doc.close()
            print(f"   Processed: {pdf_path.name}")
        except Exception as e:
            print(f"   Error reading {pdf_path.name}: {e}")
    
    return all_pages

def detect_topic(text: str) -> str:
    """Detect the primary topic of a chunk for metadata filtering."""
    text = text.lower()
    sql_keywords = ['join', 'select', 'where', 'group by', 'insert', 'update', 'delete', 'table', 'database']
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

def split_text(pages: List[dict]) -> List[Document]:
    """Splits extracted text into semantic chunks with topic tagging."""
    print(f"Splitting into chunks (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})...")
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
        keep_separator=True
    )

    documents = []
    for page in pages:
        chunks = splitter.split_text(page["text"])
        for idx, chunk in enumerate(chunks):
            documents.append(Document(
                page_content=chunk,
                metadata={
                    "source": page["source"],
                    "page": page["page"],
                    "chunk_id": idx,
                    "topic": detect_topic(chunk)  # TAGGING
                }
            ))
    
    print(f"   Generated {len(documents)} total chunks.")
    return documents

def generate_and_store(documents: List[Document]):
    """Generates embeddings and persists them to ChromaDB."""
    print(f"Loading embedding model: {EMBEDDING_MODEL}...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    print(f"Generating embeddings and saving to '{CHROMA_DIR}'...")
    start_time = time.time()
    
    try:
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            persist_directory=str(CHROMA_DIR),
            collection_name=COLLECTION_NAME
        )
        elapsed = time.time() - start_time
        print(f"   Success! Indexed {len(documents)} docs in {elapsed:.1f}s.")
    except Exception as e:
        print(f"   Error creating vector store: {e}")

def main():
    print("\n" + "="*50)
    print("PIYU RAG - EMBEDDING PIPELINE")
    print("="*50)

    # 1. Check for existing database
    if check_db_exists():
        print("WARNING: Vector DB already exists.")
        # Automatic 'y' handled by shell piping
        import shutil
        shutil.rmtree(CHROMA_DIR)
        print("Existing database cleared.")

    # 2. Load and extract
    pages = load_pdfs()
    if not pages:
        print("No text content extracted. Exiting.")
        return

    # 3. Chunk
    documents = split_text(pages)

    # 4. Embed and Store
    generate_and_store(documents)

    print("\n" + "="*50)
    print("PIPELINE COMPLETE. READY FOR RAG.")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
