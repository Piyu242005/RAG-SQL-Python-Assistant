"""
================================================================
       RAG System -- Database Initialization Script
  Processes PDF files -> Chunks -> Embeddings -> ChromaDB
================================================================

Pipeline:
  1. load_pdfs()              -- Extract text from PDFs using PyMuPDF
  2. split_documents()        -- Semantic chunking (800 chars, 150 overlap)
  3. create_embeddings()      -- Load sentence-transformers/all-MiniLM-L6-v2
  4. initialize_vector_store() -- Persist into ChromaDB (skip if exists)

Usage:
  python initialize_db.py              # Normal run (skips if DB exists)
  python initialize_db.py --force      # Force re-index from scratch
"""

import sys
import time
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional

import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from config import settings
from llm_config import OllamaManager


# ------------------------------------------------------------------
#  1. LOAD PDFs
# ------------------------------------------------------------------

def load_pdfs(pdf_dir: Path) -> List[Dict[str, Any]]:
    """
    Load and extract text from all PDF files in a directory.

    Uses PyMuPDF (fitz) for fast, accurate text extraction.
    Each page is returned as a dict with text, page number,
    source filename, and inferred doc_type.

    Args:
        pdf_dir: Path to directory containing PDF files.

    Returns:
        List of dicts: [{"text", "page", "source", "doc_type"}, ...]

    Raises:
        FileNotFoundError: If pdf_dir does not exist.
        RuntimeError: If no PDFs are found in the directory.
    """
    pdf_dir = Path(pdf_dir)
    if not pdf_dir.exists():
        raise FileNotFoundError(f"PDF directory not found: {pdf_dir}")

    pdf_files = sorted(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        raise RuntimeError(f"No PDF files found in: {pdf_dir}")

    print(f"\n[INFO] Found {len(pdf_files)} PDF file(s):")
    for f in pdf_files:
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"   - {f.name}  ({size_mb:.1f} MB)")

    all_pages: List[Dict[str, Any]] = []

    for pdf_path in pdf_files:
        try:
            doc = fitz.open(pdf_path)
            page_count = 0

            # Infer document type from filename
            name_lower = pdf_path.stem.lower()
            if "mysql" in name_lower or "sql" in name_lower:
                doc_type = "mysql"
            elif "python" in name_lower:
                doc_type = "python"
            else:
                doc_type = "general"

            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text().strip()

                if text:  # Skip blank pages
                    all_pages.append({
                        "text": text,
                        "page": page_num + 1,  # 1-indexed
                        "source": pdf_path.name,
                        "doc_type": doc_type,
                    })
                    page_count += 1

            doc.close()
            print(f"   [OK] {pdf_path.name}: {page_count} pages extracted")

        except Exception as e:
            print(f"   [FAIL] {pdf_path.name}: Failed -- {e}")
            continue  # Skip broken PDFs, process the rest

    if not all_pages:
        raise RuntimeError("No text could be extracted from any PDF.")

    print(f"\n   Total pages extracted: {len(all_pages)}")
    return all_pages


# ------------------------------------------------------------------
#  2. SPLIT DOCUMENTS
# ------------------------------------------------------------------

def split_documents(
    pages_data: List[Dict[str, Any]],
    chunk_size: int = 800,
    chunk_overlap: int = 150,
) -> List[Document]:
    """
    Split extracted page text into semantic chunks.

    Uses RecursiveCharacterTextSplitter which preserves paragraph
    and sentence boundaries for more meaningful retrieval.

    Args:
        pages_data: Output from load_pdfs().
        chunk_size: Maximum characters per chunk (default: 800).
        chunk_overlap: Overlap between consecutive chunks (default: 150).

    Returns:
        List of LangChain Document objects with metadata.

    Raises:
        ValueError: If pages_data is empty.
    """
    if not pages_data:
        raise ValueError("No page data provided for splitting.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],  # Semantic boundaries
        keep_separator=True,
    )

    documents: List[Document] = []

    for page in pages_data:
        chunks = splitter.split_text(page["text"])

        for idx, chunk_text in enumerate(chunks):
            doc = Document(
                page_content=chunk_text,
                metadata={
                    "source": page["source"],
                    "page": page["page"],
                    "chunk": idx,
                    "doc_type": page["doc_type"],
                },
            )
            documents.append(doc)

    # Summary by source
    source_counts: Dict[str, int] = {}
    for d in documents:
        src = d.metadata["source"]
        source_counts[src] = source_counts.get(src, 0) + 1

    print(f"\n[INFO] Chunking complete  (size={chunk_size}, overlap={chunk_overlap})")
    for src, count in source_counts.items():
        print(f"   - {src}: {count} chunks")
    print(f"   Total chunks: {len(documents)}")

    return documents


# ------------------------------------------------------------------
#  3. CREATE EMBEDDINGS
# ------------------------------------------------------------------

def create_embeddings(
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
) -> HuggingFaceEmbeddings:
    """
    Initialize the SentenceTransformer embedding model.

    Uses HuggingFaceEmbeddings from LangChain which wraps
    sentence-transformers for seamless integration with ChromaDB.

    Args:
        model_name: HuggingFace model identifier.

    Returns:
        HuggingFaceEmbeddings instance ready for vectorization.

    Raises:
        RuntimeError: If the model fails to load.
    """
    print(f"\n[INFO] Loading embedding model: {model_name}")
    t0 = time.time()

    try:
        embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        elapsed = time.time() - t0
        print(f"   [OK] Model loaded in {elapsed:.1f}s")
        return embeddings

    except Exception as e:
        raise RuntimeError(f"Failed to load embedding model '{model_name}': {e}")


# ------------------------------------------------------------------
#  4. INITIALIZE VECTOR STORE
# ------------------------------------------------------------------

def initialize_vector_store(
    documents: List[Document],
    embeddings: HuggingFaceEmbeddings,
    persist_directory: str = "./chroma_db",
    collection_name: str = "rag_documents",
) -> Chroma:
    """
    Create a persistent ChromaDB vector store from documents.

    Embeds all document chunks and stores them with metadata.
    The store is persisted to disk so it survives restarts.

    Args:
        documents: List of LangChain Documents to embed.
        embeddings: Embedding model instance.
        persist_directory: Path for ChromaDB persistent storage.
        collection_name: Name of the Chroma collection.

    Returns:
        Chroma vector store instance.

    Raises:
        RuntimeError: If vector store creation fails.
    """
    persist_path = Path(persist_directory)
    persist_path.mkdir(parents=True, exist_ok=True)

    print(f"\n[INFO] Creating vector store at: {persist_path.resolve()}")
    print(f"   Collection: {collection_name}")
    print(f"   Documents to embed: {len(documents)}")
    t0 = time.time()

    try:
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            persist_directory=str(persist_directory),
            collection_name=collection_name,
        )
        elapsed = time.time() - t0

        # Verify
        count = vectorstore._collection.count()
        print(f"   [OK] Vector store created in {elapsed:.1f}s")
        print(f"   Indexed documents: {count}")

        return vectorstore

    except Exception as e:
        raise RuntimeError(f"Failed to create vector store: {e}")


# ------------------------------------------------------------------
#  HELPER: Check if DB already exists
# ------------------------------------------------------------------

def _db_exists(persist_directory: str) -> bool:
    """Check if a ChromaDB database already exists on disk."""
    return (Path(persist_directory) / "chroma.sqlite3").exists()


def _get_existing_stats(
    persist_directory: str,
    embeddings: HuggingFaceEmbeddings,
    collection_name: str = "rag_documents",
) -> Optional[int]:
    """Return doc count from an existing vector store, or None on failure."""
    try:
        vs = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings,
            collection_name=collection_name,
        )
        return vs._collection.count()
    except Exception:
        return None


# ------------------------------------------------------------------
#  MAIN ORCHESTRATOR
# ------------------------------------------------------------------

def main():
    """Run the full PDF -> ChromaDB initialization pipeline."""
    parser = argparse.ArgumentParser(
        description="Initialize the RAG vector database from PDF files."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-indexing even if the database already exists.",
    )
    args = parser.parse_args()

    total_start = time.time()

    print("\n" + "=" * 60)
    print("  RAG System -- Database Initialization")
    print("=" * 60)

    # -- Step 1/5: Validate Ollama ----------------------------
    print("\n[1/5] Validating Ollama setup...")
    ollama = OllamaManager()
    status = ollama.validate_setup()

    if not status["ollama_running"]:
        print("   [FAIL] Ollama is not running!")
        print("   -> Start it with: ollama serve")
        sys.exit(1)

    if not status["model_available"]:
        model = status["configured_model"]
        print(f"   [!] Model '{model}' not found. Pulling...")
        if not ollama.pull_model():
            print(f"   [FAIL] Failed to pull model. Run: ollama pull {model}")
            sys.exit(1)

    print(f"   [OK] Ollama OK  (model: {status['configured_model']})")

    # -- Step 2/5: Check existing DB --------------------------
    persist_dir = settings.chroma_persist_directory
    print(f"\n[2/5] Checking existing database...")

    if _db_exists(persist_dir) and not args.force:
        # Load embeddings just to read stats
        emb = create_embeddings(settings.embedding_model)
        count = _get_existing_stats(persist_dir, emb)

        if count and count > 0:
            print(f"   [OK] Database already exists with {count} documents.")
            print(f"   Location: {Path(persist_dir).resolve()}")
            print(f"\n   [INFO] Skipping re-indexing. Use --force to rebuild.")
            print("\n" + "=" * 60)
            print("  [OK] Database is ready -- no action needed")
            print("=" * 60)
            return

    if args.force and _db_exists(persist_dir):
        import shutil
        print(f"   [!] --force flag set. Removing existing database...")
        shutil.rmtree(persist_dir)
        print(f"   [OK] Deleted: {persist_dir}")

    # -- Step 3/5: Load & extract PDFs ------------------------
    print(f"\n[3/5] Loading PDF documents...")
    pages = load_pdfs(settings.pdf_directory)

    # -- Step 4/5: Chunk documents ----------------------------
    print(f"\n[4/5] Splitting into semantic chunks...")
    documents = split_documents(
        pages,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )

    # -- Step 5/5: Embed & store ------------------------------
    print(f"\n[5/5] Creating embeddings & vector store...")
    embeddings = create_embeddings(settings.embedding_model)
    initialize_vector_store(
        documents=documents,
        embeddings=embeddings,
        persist_directory=persist_dir,
    )

    # -- Done -------------------------------------------------
    total_elapsed = time.time() - total_start

    print("\n" + "=" * 60)
    print(f"  [OK] INITIALIZATION COMPLETE  ({total_elapsed:.1f}s)")
    print("=" * 60)
    print("\n  Next steps:")
    print("    1. Start backend:   python main.py")
    print("    2. API docs:        http://localhost:8000/docs")
    print("    3. Start frontend:  cd ../frontend && npm run dev")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
