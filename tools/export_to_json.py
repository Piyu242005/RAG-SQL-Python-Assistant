"""
Piyu RAG - JSON Export Tool
Processes PDFs into chunks and exports them to a structured JSON file.
"""

import os
import sys
import json
from pathlib import Path

# Add backend to path so we can import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from config import settings

import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Configuration (Aligned with production settings)
PDF_DIR = settings.pdf_directory
EXPORT_DIR = Path("../exports")
CHUNK_SIZE = settings.chunk_size
CHUNK_OVERLAP = settings.chunk_overlap

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

def load_and_chunk():
    """Extracts text from PDFs and splits into chunks with topic tagging."""
    if not PDF_DIR.exists():
        print(f"Error: Directory '{PDF_DIR}' not found.")
        return []

    pdf_files = list(PDF_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"Warning: No PDF files found in '{PDF_DIR}'.")
        return []

    print(f"Processing {len(pdf_files)} PDFs for JSON export...")
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
        keep_separator=True
    )

    all_chunks = []
    chunk_counter = 0

    for pdf_path in pdf_files:
        try:
            doc = fitz.open(pdf_path)
            for page_num, page in enumerate(doc):
                text = page.get_text().strip()
                if text:
                    chunks = splitter.split_text(text)
                    for idx, chunk_text in enumerate(chunks):
                        all_chunks.append({
                            "id": f"chunk_{chunk_counter}",
                            "source": pdf_path.name,
                            "page": page_num + 1,
                            "topic": detect_topic(chunk_text),  # TUNED FOR RAG
                            "chunk_index": idx,
                            "content": chunk_text,
                            "char_count": len(chunk_text)
                        })
                        chunk_counter += 1
            doc.close()
            print(f"   Processed: {pdf_path.name}")
        except Exception as e:
            print(f"   Error reading {pdf_path.name}: {e}")
    
    return all_chunks

def save_json(data):
    """Saves the chunk data to a JSON file in the exports folder."""
    EXPORT_DIR.mkdir(exist_ok=True)
    output_file = EXPORT_DIR / "transcription_chunks.json"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"\nSuccessfully exported {len(data)} chunks to: {output_file}")
    except Exception as e:
        print(f"Error saving JSON: {e}")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("PIYU RAG - JSON CHUNK EXPORTER")
    print("="*50)
    
    chunks = load_and_chunk()
    if chunks:
        save_json(chunks)
    
    print("="*50 + "\n")
