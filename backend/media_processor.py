"""
Media processing module for Audio and Video RAG.
Uses FFmpeg for extraction and OpenAI Whisper for transcription.
"""

import os
import subprocess
import whisper
from pathlib import Path
from typing import List, Dict, Optional
from langchain_core.documents import Document
from config import settings

class MediaProcessor:
    """Handles video and audio transcription for RAG ingestion."""
    
    def __init__(self, model_size: str = "base"):
        """Initialize MediaProcessor with a specific Whisper model."""
        print(f"Loading Whisper transcription model ({model_size})...")
        self.model = whisper.load_model(model_size)
        print("[OK] Transcription model ready.")

    def extract_audio(self, input_file: Path) -> Path:
        """Extracts audio from video files using FFmpeg."""
        output_file = input_file.with_suffix(".wav")
        
        print(f"   Extracting audio from {input_file.name}...")
        command = [
            "ffmpeg", "-i", str(input_file),
            "-ar", "16000", "-ac", "1", "-y",
            str(output_file)
        ]
        
        try:
            subprocess.run(command, check=True, capture_output=True)
            return output_file
        except subprocess.CalledProcessError as e:
            print(f"[X] FFmpeg error: {e.stderr.decode()}")
            raise RuntimeError("Failed to extract audio using FFmpeg.")

    def transcribe(self, media_path: Path) -> str:
        """Transcribes audio/video to text using Whisper."""
        temp_audio = None
        
        # If it's a video file, extract audio first
        if media_path.suffix.lower() in ['.mp4', '.mkv', '.avi', '.mov']:
            temp_audio = self.extract_audio(media_path)
            process_path = str(temp_audio)
        else:
            process_path = str(media_path)

        print(f"   Transcribing {media_path.name} (this may take a moment)...")
        result = self.model.transcribe(process_path)
        
        # Cleanup temp audio file
        if temp_audio and temp_audio.exists():
            temp_audio.unlink()
            
        return result["text"]

    def process_media_file(self, file_path: Path, doc_type: str) -> List[Document]:
        """Transcribes media and creates LangChain Document objects."""
        from document_processor import DocumentProcessor
        
        text = self.transcribe(file_path)
        
        # Reuse existing chunking logic from DocumentProcessor
        doc_processor = DocumentProcessor()
        
        # Mocking a single page structure for the media file
        pages_data = [{
            "text": text,
            "page_number": 1,
            "source": file_path.name
        }]
        
        documents = doc_processor.chunk_documents(pages_data, doc_type)
        print(f"[OK] Processed media into {len(documents)} text chunks.")
        
        return documents

# Example usage
if __name__ == "__main__":
    # Test script
    processor = MediaProcessor()
    # Path to a test file if available
    test_file = Path("test_media.mp4")
    if test_file.exists():
        docs = processor.process_media_file(test_file, "multimodal")
        print(f"Extracted {len(docs)} documents.")
