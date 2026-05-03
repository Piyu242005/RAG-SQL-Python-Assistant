"""
Piyu RAG - Media Ingestion Tool
Transcribes audio/video files and adds them to the ChromaDB vector store.
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from config import settings
from media_processor import MediaProcessor
from vector_store import VectorStoreManager

def main():
    print("\n" + "="*50)
    print("🎥 PIYU RAG - MEDIA INGESTION PIPELINE")
    print("="*50)

    # Ensure media directory exists
    media_dir = settings.media_directory
    media_dir.mkdir(parents=True, exist_ok=True)

    media_files = []
    supported_extensions = ['.mp4', '.mp3', '.mkv', '.wav', '.mov', '.avi']
    
    for ext in supported_extensions:
        media_files.extend(list(media_dir.glob(f"*{ext}")))

    if not media_files:
        print(f"No media files found in {media_dir}")
        print("Please add .mp4, .mp3, etc. files to the folder and run again.")
        return

    print(f"Found {len(media_files)} media file(s) for processing.")
    
    processor = MediaProcessor(model_size="base")
    vector_manager = VectorStoreManager()
    
    for media_path in media_files:
        print(f"\nProcessing: {media_path.name}")
        try:
            # Detect type for metadata
            doc_type = "multimodal_video" if media_path.suffix.lower() == '.mp4' else "multimodal_audio"
            
            # Transcribe and Chunk
            documents = processor.process_media_file(media_path, doc_type)
            
            # Add to Vector Store
            vector_manager.add_documents(documents)
            print(f"Successfully indexed {len(documents)} chunks from {media_path.name}")
            
        except Exception as e:
            print(f"Error processing {media_path.name}: {e}")

    print("\n" + "="*50)
    print("PIPELINE COMPLETE. Multimodal content is ready for chat!")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
