import os
import sys
import json
from pathlib import Path

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from document_processor import DocumentProcessor
from vector_store import VectorStoreManager
from evals.runner import run_evaluation

def run_experiment(chunk_size, chunk_overlap):
    print(f"\n{'='*60}")
    print(f" EXPERIMENT: Chunk Size {chunk_size}, Overlap {chunk_overlap}")
    print(f"{'='*60}")
    
    # 1. Reset Vector Store
    vsm = VectorStoreManager()
    vsm.reset_vectorstore()
    
    # 2. Process documents with new settings
    processor = DocumentProcessor(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    documents = processor.process_all_pdfs()
    
    # 3. Initialize Vector Store with new documents
    vsm.initialize_vectorstore(documents=documents)
    
    # 4. Run Evaluation
    # We'll run the evaluation runner logic here or call it
    # For now, let's just return the result from a modified runner
    # (I'll assume run_evaluation returns the metrics dict for simplicity in this script)
    # Actually I'll just run the script and read the report.json
    
    os.system("python evals/runner.py")
    
    with open("evals/report.json", "r") as f:
        report = json.load(f)
        
    return report["metrics"]

if __name__ == "__main__":
    configs = [
        (500, 50),
        (1000, 100),
        (1500, 200)
    ]
    
    results = {}
    for size, overlap in configs:
        metrics = run_experiment(size, overlap)
        results[f"S{size}_O{overlap}"] = metrics
        
    print("\n" + "=" * 60)
    print(" EXPERIMENT RESULTS TABLE")
    print("=" * 60)
    print(f"{'Config':<15} | {'Recall@3':<10} | {'Latency':<10}")
    print("-" * 40)
    for cfg, m in results.items():
        print(f"{cfg:<15} | {m['avg_recall@3']:<10.2%} | {m['avg_latency']:<10.2f}s")
    print("=" * 60)
