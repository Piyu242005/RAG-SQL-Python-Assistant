"""Initialize database by processing PDFs and creating vector store."""
import sys
from document_processor import DocumentProcessor
from vector_store import VectorStoreManager
from llm_config import OllamaManager

def main():
    """Main initialization function."""
    print("\n" + "=" * 60)
    print("🚀 RAG System Database Initialization")
    print("=" * 60)
    
    # Step 1: Validate Ollama
    print("\n📋 Step 1: Validating Ollama setup...")
    ollama_manager = OllamaManager()
    status = ollama_manager.validate_setup()
    
    if not status['ollama_running']:
        print("\n❌ ERROR: Ollama is not running!")
        print("\nPlease start Ollama:")
        print("  1. Open a terminal")
        print("  2. Run: ollama serve")
        print("  3. Run this script again")
        sys.exit(1)
    
    if not status['model_available']:
        print(f"\n⚠️  Model '{status['configured_model']}' not found!")
        print(f"\nAttempting to pull model...")
        if not ollama_manager.pull_model():
            print("\n❌ ERROR: Failed to pull model!")
            print(f"\nPlease manually pull the model:")
            print(f"  ollama pull {status['configured_model']}")
            sys.exit(1)
    
    print("✅ Ollama setup validated")
    
    # Step 2: Process PDFs
    print("\n📋 Step 2: Processing PDF documents...")
    processor = DocumentProcessor()
    
    try:
        documents = processor.process_all_pdfs()
        
        if not documents:
            print("\n❌ ERROR: No documents were processed!")
            print("Please ensure PDF files exist in the workspace:")
            print("  - MySQL Handbook.pdf")
            print("  - The Ultimate Python Handbook.pdf")
            sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ ERROR processing documents: {str(e)}")
        sys.exit(1)
    
    # Step 3: Initialize Vector Store
    print("\n📋 Step 3: Initializing vector store...")
    print("(This may take a few minutes for embedding generation)")
    
    try:
        vector_manager = VectorStoreManager()
        
        # Reset if exists
        if vector_manager._vectorstore_exists():
            print("⚠️  Existing vector store found. Resetting...")
            vector_manager.reset_vectorstore()
        
        # Create new vector store
        vector_manager.initialize_vectorstore(documents)
        
        # Verify
        stats = vector_manager.get_stats()
        print(f"\n✅ Vector store created successfully!")
        print(f"   Total documents: {stats['total_documents']}")
        print(f"   Location: {stats['persist_directory']}")
        
    except Exception as e:
        print(f"\n❌ ERROR initializing vector store: {str(e)}")
        sys.exit(1)
    
    # Step 4: Test Query
    print("\n📋 Step 4: Testing RAG pipeline...")
    
    try:
        from rag_pipeline import RAGPipeline
        
        rag = RAGPipeline()
        test_query = "What is a SQL SELECT statement?"
        
        print(f"Test query: '{test_query}'")
        result = rag.query(test_query)
        
        if result['success']:
            print("\n✅ RAG pipeline test successful!")
            print(f"\nSample answer preview:")
            print(result['answer'][:200] + "...")
        else:
            print(f"\n⚠️  RAG pipeline test failed: {result.get('error')}")
    
    except Exception as e:
        print(f"\n⚠️  Could not test RAG pipeline: {str(e)}")
        print("You can test it later by starting the API server.")
    
    # Success
    print("\n" + "=" * 60)
    print("✅ INITIALIZATION COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Start the backend API:")
    print("     cd backend")
    print("     python main.py")
    print("     or: uvicorn main:app --reload")
    print("\n  2. Test the API:")
    print("     http://localhost:8000/docs")
    print("\n  3. Start the frontend:")
    print("     cd frontend")
    print("     npm run dev")
    print("=" * 60)

if __name__ == "__main__":
    main()
