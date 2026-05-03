"""
Piyu RAG - Embedding Inspector & Visualizer
Exports vectors to CSV and generates a 2D semantic map.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from vector_store import VectorStoreManager

def export_to_csv():
    """Exports all stored chunks, metadata, and embeddings to a CSV file."""
    print("Connecting to ChromaDB...")
    manager = VectorStoreManager()
    vectorstore = manager.initialize_vectorstore()
    
    # Retrieve all data including embeddings
    data = vectorstore.get(include=['documents', 'metadatas', 'embeddings'])
    
    if not data['ids']:
        print("No data found in the vector store.")
        return

    print(f"Processing {len(data['ids'])} documents...")
    
    # Create DataFrame
    df = pd.DataFrame({
        'id': data['ids'],
        'source': [m.get('source') for m in data['metadatas']],
        'page': [m.get('page') for m in data['metadatas']],
        'content': data['documents'],
        'embedding_preview': [str(e[:5]) + "..." for e in data['embeddings']]
    })
    
    output_file = "embeddings_audit.csv"
    df.to_csv(output_file, index=False)
    print(f"Exported to: {output_file}")
    return data

def visualize_embeddings(data):
    """Generates a 2D T-SNE visualization of the embeddings."""
    print("Generating 2D semantic visualization...")
    
    embeddings = np.array(data['embeddings'])
    sources = [m.get('source', 'Unknown') for m in data['metadatas']]
    
    # Reduce dimensions to 2D using T-SNE
    # Ensure perplexity is smaller than the number of samples
    n_samples = len(embeddings)
    perplexity = min(30, max(1, n_samples - 1))
    
    tsne = TSNE(n_components=2, random_state=42, perplexity=perplexity)
    embeddings_2d = tsne.fit_transform(embeddings)
    
    plt.figure(figsize=(12, 8))
    
    # Color by source file
    unique_sources = list(set(sources))
    colors = plt.cm.rainbow(np.linspace(0, 1, len(unique_sources)))
    
    for source, color in zip(unique_sources, colors):
        indices = [i for i, s in enumerate(sources) if s == source]
        plt.scatter(
            embeddings_2d[indices, 0], 
            embeddings_2d[indices, 1], 
            c=[color], 
            label=source, 
            alpha=0.6, 
            edgecolors='w', 
            s=100
        )
    
    plt.title("Semantic Map of Piyu AI Assistant Documents", fontsize=15)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.3)
    
    output_img = "embedding_visualization.png"
    plt.savefig(output_img)
    print(f"Visualization saved to: {output_img}")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("PIYU RAG - EMBEDDING INSPECTOR")
    print("="*50)
    
    # 1. Export
    data = export_to_csv()
    
    # 2. Visualize
    if data:
        try:
            visualize_embeddings(data)
        except Exception as e:
            print(f"Could not generate visualization: {e}")
            print("Tip: Ensure matplotlib and scikit-learn are installed.")
    
    print("="*50 + "\n")
