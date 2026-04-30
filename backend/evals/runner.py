import sys
import os
import json
import time
from pathlib import Path

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag_pipeline import RAGPipeline
from evals.metrics import calculate_recall, calculate_citation_accuracy

def run_evaluation():
    print("=" * 60)
    print(" RAG Evaluation Runner")
    print("=" * 60)
    
    # Load dataset
    dataset_path = Path(__file__).parent / "dataset.json"
    if not dataset_path.exists():
        print(f"[X] Dataset not found at {dataset_path}")
        return
    
    with open(dataset_path, "r") as f:
        dataset = json.load(f)
    
    print(f"[OK] Loaded {len(dataset)} evaluation pairs")
    
    # Initialize RAG
    try:
        rag = RAGPipeline()
    except Exception as e:
        print(f"[X] Failed to initialize RAG pipeline: {str(e)}")
        print("Note: Ensure Ollama is running if evaluating generation.")
        return

    results = []
    total_recall = 0
    total_citation_acc = 0
    
    for i, item in enumerate(dataset, 1):
        question = item["question"]
        expected_page = item["expected_page"]
        expected_source = item["expected_source"]
        
        print(f"\n[{i}/{len(dataset)}] Evaluating: {question}")
        
        start_time = time.time()
        
        # 1. Evaluate Retrieval
        try:
            retrieved_docs = rag.retriever.invoke(question)
            # Convert LangChain docs to dicts for metrics
            retrieved_data = [{"metadata": doc.metadata} for doc in retrieved_docs]
            
            recall_score = calculate_recall(retrieved_data, expected_page, expected_source, k=3)
            total_recall += recall_score
        except Exception as e:
            print(f"  [X] Retrieval error: {str(e)}")
            recall_score = 0
            retrieved_docs = []
        
        # 2. Evaluate Generation & Citations
        try:
            query_result = rag.query(question)
            answer = query_result.get("answer", "")
            citations = query_result.get("sources", [])
            
            citation_score = calculate_citation_accuracy(answer, citations, expected_page, expected_source)
            total_citation_acc += citation_score
        except Exception as e:
            print(f"  [X] Generation error: {str(e)}")
            citation_score = 0
            answer = "ERROR"
        
        latency = time.time() - start_time
        
        results.append({
            "question": question,
            "recall@3": recall_score,
            "citation_acc": citation_score,
            "latency": round(latency, 2)
        })
        
        print(f"  > Recall@3: {recall_score}")
        print(f"  > Citation Acc: {citation_score}")
        print(f"  > Latency: {round(latency, 2)}s")

    # Final Report
    avg_recall = total_recall / len(dataset)
    avg_citation_acc = total_citation_acc / len(dataset)
    avg_latency = sum(r["latency"] for r in results) / len(dataset)
    
    print("\n" + "=" * 60)
    print(" EVALUATION SUMMARY")
    print("=" * 60)
    print(f" Average Recall@3:     {avg_recall:.2%}")
    print(f" Average Citation Acc: {avg_citation_acc:.2%}")
    print(f" Average Latency:      {avg_latency:.2f}s")
    print("=" * 60)
    
    # Save results to file
    report_path = Path(__file__).parent / "report.json"
    with open(report_path, "w") as f:
        json.dump({
            "metrics": {
                "avg_recall@3": avg_recall,
                "avg_citation_acc": avg_citation_acc,
                "avg_latency": avg_latency
            },
            "detailed_results": results
        }, f, indent=2)
    print(f"[OK] Full report saved to {report_path}")

if __name__ == "__main__":
    run_evaluation()
