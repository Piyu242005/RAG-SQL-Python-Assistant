from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from rag.ingestion import IngestionPipeline
import os
import shutil
import uuid

router = APIRouter(tags=["Documents"])
ingestion_pipeline = IngestionPipeline()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/documents/upload")
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Process in background
    background_tasks.add_task(ingestion_pipeline.process, file_path)
    
    return {
        "id": file_id,
        "filename": file.filename,
        "status": "uploading",
        "message": "Document uploaded and processing in background"
    }

@router.get("/documents/health")
def doc_health():
    return {"status": "ok"}
