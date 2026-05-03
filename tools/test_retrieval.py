"""
Piyu RAG - Retrieval Demonstration
Shows how the system pulls the top matching chunks for a given lecture query.
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from vector_store import VectorStoreManager

def demo_retrieval(query: str):
    print("\n" + "="*70)
    print(f"Retriever Demo: '{query}'")
    print("="*70)
    
    manager = VectorStoreManager()
    
    # We pull the top 3 most relevant chunks
    docs = manager.similarity_search(query, k=3)
    
    print("\n[TOP MATCHING CHUNKS]")
    print("-" * 30)
    for i, doc in enumerate(docs, 1):
        print(f"RANK {i}:")
        print(f"   Source: {doc.metadata.get('source')}")
        print(f"   Page:   {doc.metadata.get('page')}")
        print(f"   Topic:  {doc.metadata.get('topic')}")
        print(f"   Content Snippet: {doc.page_content[:150]}...")
        print("-" * 30)

if __name__ == "__main__":
    # Sample lecture-style query
    query = "Explain how inner joins work in MySQL and give an example."
    demo_retrieval(query)
