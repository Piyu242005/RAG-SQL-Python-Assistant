"""
Piyu RAG - Evaluation & Benchmarking Pipeline
Measures Recall@K and Retrieval Latency for production monitoring.
"""

import os
import sys
import time
import json
from typing import List, Dict

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from vector_store import VectorStoreManager

# Define Ground Truth (Query -> Expected Source/Topic)
TEST_SUITE = [
    {
        "query": "How do I perform an inner join in MySQL?",
        "expected_source": "MySQL Handbook.pdf",
        "expected_topic": "sql_joins"
    },
    {
        "query": "What is a Python decorator and how is it used?",
        "expected_source": "The Ultimate Python Handbook.pdf",
        "expected_topic": "python_decorators"
    },
    {
        "query": "Explain SQL SELECT statement syntax.",
        "expected_source": "MySQL Handbook.pdf",
        "expected_topic": "sql_queries"
    },
    {
        "query": "How to handle exceptions in Python?",
        "expected_source": "The Ultimate Python Handbook.pdf",
        "expected_topic": "python_general"
    }
]

def run_eval():
    print("\n" + "="*50)
    print("PIYU RAG - EVALUATION RUN")
    print("="*50)
    
    manager = VectorStoreManager()
    results = []
    
    total_latency = 0
    total_recall_at_1 = 0
    total_recall_at_5 = 0
    
    for test in TEST_SUITE:
        print(f"\nEvaluating Query: '{test['query']}'")
        
        start_time = time.time()
        # Perform retrieval
        retrieved_docs = manager.similarity_search(test['query'], k=5)
        latency = time.time() - start_time
        total_latency += latency
        
        # Check Recall
        found_at_1 = False
        found_at_5 = False
        
        for i, doc in enumerate(retrieved_docs):
            source_match = test['expected_source'] in doc.metadata.get('source', '')
            topic_match = test['expected_topic'] == doc.metadata.get('topic', '')
            
            if source_match:
                if i == 0: found_at_1 = True
                found_at_5 = True
                break
        
        if found_at_1: total_recall_at_1 += 1
        if found_at_5: total_recall_at_5 += 1
        
        print(f"   Latency: {latency:.4f}s")
        print(f"   Recall@1: {'SUCCESS' if found_at_1 else 'FAIL'}")
        print(f"   Recall@5: {'SUCCESS' if found_at_5 else 'FAIL'}")
        
        results.append({
            "query": test['query'],
            "latency": latency,
            "recall_at_1": found_at_1,
            "recall_at_5": found_at_5
        })

    # Summary Statistics
    count = len(TEST_SUITE)
    print("\n" + "="*50)
    print("FINAL BENCHMARK SUMMARY")
    print("="*50)
    print(f"Average Latency: {total_latency/count:.4f}s")
    print(f"Mean Recall@1:   {(total_recall_at_1/count)*100:.1f}%")
    print(f"Mean Recall@5:   {(total_recall_at_5/count)*100:.1f}%")
    print("="*50 + "\n")

if __name__ == "__main__":
    run_eval()
