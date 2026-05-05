"""
================================================================
       RAG System -- Database Initialization Script
  Processes PDF files -> Chunks -> Embeddings -> ChromaDB
================================================================

Pipeline:
  1. Validate Ollama                -- Ensure LLM backend is reachable
  2. Reset vector store (optional)  -- Wipe stale data via VectorStoreManager
  3. Load & chunk PDFs              -- DocumentProcessor with settings.chunk_size/overlap
  4. Embed & persist                -- VectorStoreManager.initialize_vectorstore()
  5. Verify & report                -- Log doc count, chunk count, vector count

Usage:
  python initialize_db.py              # Normal run (skips if DB exists)
  python initialize_db.py --force      # Wipe existing DB and re-index from scratch
  python initialize_db.py --force --semantic  # Semantic chunking (slow, high quality)
"""

import sys
import time
import logging
import argparse
import shutil
from pathlib import Path
from typing import List

from langchain_core.documents import Document

from config import settings
from llm_config import OllamaManager
from document_processor import DocumentProcessor
from vector_store import VectorStoreManager


# ──────────────────────────────────────────────────────────────
#  Logging setup  (structured, production-safe)
# ──────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("initialize_db")


# ──────────────────────────────────────────────────────────────
#  Helper: banner
# ──────────────────────────────────────────────────────────────

def _banner(title: str) -> None:
    logger.info("=" * 60)
    logger.info(f"  {title}")
    logger.info("=" * 60)


# ──────────────────────────────────────────────────────────────
#  Step 1: Validate Ollama
# ──────────────────────────────────────────────────────────────

def _validate_ollama() -> None:
    """Ensure Ollama is running and the configured model is available."""
    logger.info("[1/5] Validating Ollama setup...")
    ollama = OllamaManager()
    status = ollama.validate_setup()

    if not status["ollama_running"]:
        logger.error("Ollama is NOT running. Start it with: ollama serve")
        sys.exit(1)

    if not status["model_available"]:
        model = status["configured_model"]
        logger.warning(f"Model '{model}' not found locally. Pulling...")
        if not ollama.pull_model():
            logger.error(f"Failed to pull model '{model}'. Run: ollama pull {model}")
            sys.exit(1)

    logger.info(f"[OK] Ollama ready  (model: {status['configured_model']})")


# ──────────────────────────────────────────────────────────────
#  Step 2: Reset vector store
# ──────────────────────────────────────────────────────────────

def _reset_vector_store(manager: VectorStoreManager) -> None:
    """
    Wipe the existing ChromaDB collection and any BM25 cache so that no
    stale embeddings survive into the new index.
    """
    persist_path = Path(manager.persist_directory)

    if not persist_path.exists():
        logger.info("[2/5] No existing database found -- nothing to delete.")
        return

    logger.info(f"[2/5] Removing existing vector store at: {persist_path.resolve()}")

    # Delegate to VectorStoreManager for a clean reset
    try:
        manager.reset_vectorstore()
        logger.info("[OK] Vector store deleted successfully.")
    except Exception as exc:
        logger.error(f"Failed to delete vector store: {exc}")
        raise

    # Belt-and-suspenders: remove any leftover BM25 cache
    bm25_cache = persist_path / "bm25_retriever.pkl"
    if bm25_cache.exists():
        bm25_cache.unlink(missing_ok=True)
        logger.info("[OK] BM25 cache cleared.")


# ──────────────────────────────────────────────────────────────
#  Step 3: Process PDFs
# ──────────────────────────────────────────────────────────────

def _process_pdfs(use_semantic: bool) -> List[Document]:
    """
    Load every PDF from settings.pdf_directory, chunk them with the
    chunking strategy specified in settings (CHUNK_SIZE / CHUNK_OVERLAP),
    and return a flat list of LangChain Documents.
    """
    strategy = "SemanticChunker" if use_semantic else "RecursiveCharacterTextSplitter"
    logger.info(
        f"[3/5] Processing PDFs  "
        f"(strategy={strategy}, chunk_size={settings.chunk_size}, "
        f"chunk_overlap={settings.chunk_overlap})"
    )

    pdf_dir = Path(settings.pdf_directory)
    if not pdf_dir.exists():
        logger.error(f"PDF directory not found: {pdf_dir.resolve()}")
        sys.exit(1)

    pdf_files = sorted(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        logger.error(f"No PDF files found in: {pdf_dir.resolve()}")
        sys.exit(1)

    logger.info(f"Found {len(pdf_files)} PDF file(s): {[f.name for f in pdf_files]}")

    processor = DocumentProcessor(use_semantic=use_semantic)

    all_documents: List[Document] = []
    docs_processed = 0
    failed_files: List[str] = []

    for pdf_path in pdf_files:
        try:
            doc_type = processor._detect_topic("", source=pdf_path.name)
            docs = processor.process_pdf(pdf_path, doc_type)

            if not docs:
                logger.warning(f"[SKIP] No extractable text in: {pdf_path.name}")
                continue

            all_documents.extend(docs)
            docs_processed += 1
            logger.info(
                f"  [{docs_processed}/{len(pdf_files)}] {pdf_path.name} "
                f"-> {len(docs)} chunk(s)"
            )

        except Exception as exc:
            logger.error(f"[FAIL] Error processing {pdf_path.name}: {exc}")
            failed_files.append(pdf_path.name)
            # Continue with remaining PDFs; do not abort the full run

    # ── Summary ──
    logger.info("-" * 50)
    logger.info(f"Documents processed : {docs_processed}/{len(pdf_files)}")
    logger.info(f"Total chunks created: {len(all_documents)}")
    if failed_files:
        logger.warning(f"Failed files ({len(failed_files)}): {failed_files}")

    if not all_documents:
        logger.error(
            "No chunks were produced. Check that your PDFs contain extractable text."
        )
        sys.exit(1)

    return all_documents


# ──────────────────────────────────────────────────────────────
#  Step 4 + 5: Embed & persist via VectorStoreManager
# ──────────────────────────────────────────────────────────────

def _build_vector_store(
    manager: VectorStoreManager,
    documents: List[Document],
) -> int:
    """
    Embed all chunks and persist them through VectorStoreManager.
    Returns the total number of vectors stored.
    """
    logger.info(f"[4/5] Loading embedding model: {settings.embedding_model}")

    t0 = time.time()
    logger.info(f"[5/5] Embedding {len(documents)} chunk(s) and persisting to ChromaDB...")

    try:
        vectorstore = manager.initialize_vectorstore(documents=documents)
        elapsed = time.time() - t0

        # Verify stored count via a direct collection call
        total_vectors: int = vectorstore._collection.count()
        logger.info(f"[OK] Vector store built in {elapsed:.1f}s")
        logger.info(f"Total vectors stored: {total_vectors}")
        logger.info(f"Persist directory   : {Path(manager.persist_directory).resolve()}")

        return total_vectors

    except Exception as exc:
        logger.error(f"Failed to create vector store: {exc}")
        raise


# ──────────────────────────────────────────────────────────────
#  MAIN ORCHESTRATOR
# ──────────────────────────────────────────────────────────────

def main() -> None:
    """Run the full PDF -> ChromaDB initialization pipeline."""

    parser = argparse.ArgumentParser(
        description="Initialize the RAG vector database from PDF files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-indexing even if the database already exists.",
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Alias for --force.",
    )
    parser.add_argument(
        "--semantic",
        action="store_true",
        help="Use SemanticChunker instead of RecursiveCharacterTextSplitter (slow).",
    )
    args = parser.parse_args()

    force_rebuild = args.force or args.rebuild
    total_start = time.time()

    _banner("RAG System -- Database Initialization")
    logger.info(
        f"Config  ->  CHUNK_SIZE={settings.chunk_size}  "
        f"CHUNK_OVERLAP={settings.chunk_overlap}"
    )

    # ── Step 1: Validate Ollama ──────────────────────────────
    _validate_ollama()

    # ── Step 2: Handle existing DB ───────────────────────────
    manager = VectorStoreManager()
    db_sqlite = Path(manager.persist_directory) / "chroma.sqlite3"

    if db_sqlite.exists() and not force_rebuild:
        # Peek at current count without re-embedding anything
        stats = manager.get_stats()
        existing_count = stats.get("total_documents", 0)
        logger.info(
            f"[2/5] Existing database found with {existing_count} vector(s)."
        )
        logger.info("      Use --force to wipe and rebuild from scratch.")
        _banner("[OK] Database is already populated -- no action needed")
        return

    if force_rebuild and db_sqlite.exists():
        _reset_vector_store(manager)
    else:
        logger.info("[2/5] No existing database -- fresh build.")

    # ── Step 3: Process PDFs ─────────────────────────────────
    documents = _process_pdfs(use_semantic=args.semantic)

    # ── Steps 4 + 5: Embed & store ───────────────────────────
    total_vectors = _build_vector_store(manager, documents)

    # ── Done ─────────────────────────────────────────────────
    total_elapsed = time.time() - total_start

    _banner(f"[OK] INITIALIZATION COMPLETE  ({total_elapsed:.1f}s)")
    logger.info(f"  Documents processed : {len(set(d.metadata['source'] for d in documents))}")
    logger.info(f"  Chunks created      : {len(documents)}")
    logger.info(f"  Vectors stored      : {total_vectors}")
    logger.info("")
    logger.info("  Next steps:")
    logger.info("    1. Start backend :  python main.py")
    logger.info("    2. API docs      :  http://localhost:8000/docs")
    logger.info("    3. Start frontend:  cd ../frontend && npm run dev")
    _banner("=" * 56)


if __name__ == "__main__":
    main()
