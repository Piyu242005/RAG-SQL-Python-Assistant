import sys
# Add backend to path so we can import vector_store
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

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
    
    # Save to exports folder
    output_dir = Path("../exports")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "embeddings_audit.csv"
    df.to_csv(output_file, index=False)
    print(f"Exported to: {output_file}")
    return data

import umap

def visualize_embeddings(data):
    """Generates a 2D UMAP visualization of the embeddings (Upgrade from TSNE)."""
    print("🎨 Generating 2D UMAP semantic visualization...")
    
    embeddings = np.array(data['embeddings'])
    sources = [m.get('source', 'Unknown') for m in data['metadatas']]
    topics = [m.get('topic', 'General') for m in data['metadatas']]
    
    # Using UMAP for better cluster separation
    reducer = umap.UMAP(
        n_neighbors=15,
        min_dist=0.1,
        n_components=2,
        random_state=42
    )
    embeddings_2d = reducer.fit_transform(embeddings)
    
    plt.figure(figsize=(14, 9))
    
    # Color by topic for better insight
    unique_topics = list(set(topics))
    colors = plt.cm.get_cmap('tab10', len(unique_topics))
    
    for i, topic in enumerate(unique_topics):
        indices = [idx for idx, t in enumerate(topics) if t == topic]
        plt.scatter(
            embeddings_2d[indices, 0], 
            embeddings_2d[indices, 1], 
            label=topic, 
            alpha=0.7, 
            edgecolors='none', 
            s=80
        )
    
    plt.title("Semantic Topic Clusters (UMAP Visualization)", fontsize=16, pad=20)
    plt.xlabel("UMAP Dimension 1")
    plt.ylabel("UMAP Dimension 2")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title="Topics")
    plt.grid(True, linestyle='--', alpha=0.2)
    plt.tight_layout()
    
    output_dir = Path("../exports")
    output_img = output_dir / "umap_visualization.png"
    plt.savefig(output_img, dpi=300)
    print(f"✅ UMAP Visualization saved to: {output_img}")

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
