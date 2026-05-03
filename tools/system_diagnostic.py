"""
Piyu RAG - System Diagnostic Tool
Verifies connectivity between Backend, Vector DB, and Ollama.
"""

import os
import sys
import requests
from pathlib import Path

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from config import settings
from vector_store import VectorStoreManager

def check_system():
    print("\n" + "="*50)
    print("SYSTEM DIAGNOSTIC")
    print("="*50)

    # 1. Check Ollama
    print("\n[1] Checking Ollama LLM...")
    try:
        response = requests.get(f"{settings.ollama_base_url}/api/tags")
        if response.status_code == 200:
            models = [m['name'] for m in response.json().get('models', [])]
            print(f"   [OK] Ollama is active.")
            print(f"   [OK] Available Models: {models}")
            if settings.ollama_model in [m.split(':')[0] for m in models]:
                 print(f"   [OK] Required model '{settings.ollama_model}' is present.")
            else:
                 print(f"   [!] Warning: Model '{settings.ollama_model}' not found in Ollama list.")
        else:
            print(f"   [X] Ollama returned status: {response.status_code}")
    except Exception as e:
        print(f"   [X] Ollama Connection Failed: {e}")

    # 2. Check Vector Database (ChromaDB)
    print("\n[2] Checking Vector Database (ChromaDB)...")
    try:
        manager = VectorStoreManager()
        # Test connection by getting stats
        stats = manager.get_stats()
        if "error" in stats:
             print(f"   [X] ChromaDB Error: {stats['error']}")
        else:
             print(f"   [OK] ChromaDB is active.")
             print(f"   [OK] Persist Directory: {stats['persist_directory']}")
             
             # 3. Check Indexing Status
             count = stats.get('total_documents', 0)
             if count > 0:
                 print(f"   [OK] Documents Indexed: {count} chunks found.")
             else:
                 print(f"   [!] Warning: Vector store is empty (0 chunks).")
    except Exception as e:
        print(f"   [X] Vector DB Initialization Failed: {e}")

    # 4. Check Redis Caching
    print("\n[4] Checking Redis Caching...")
    try:
        import redis
        r = redis.from_url(settings.redis_url)
        if r.ping():
            print(f"   [OK] Redis is active.")
        else:
            print(f"   [X] Redis Ping Failed.")
    except Exception as e:
        print(f"   [X] Redis Connection Failed: {e}")

    print("\n" + "="*50)
    print("DIAGNOSTIC COMPLETE")
    print("="*50 + "\n")

if __name__ == "__main__":
    check_system()
