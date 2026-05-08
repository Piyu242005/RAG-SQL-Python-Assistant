from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from schemas.chat import InitializeResponse # I should move this to a more general schema file
from api.deps import get_document_service
from services.document import DocumentService

router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.get("/stats")
async def get_stats(service: DocumentService = Depends(get_document_service)):
    return service.get_stats()

@router.post("/reset")
async def reset_system(service: DocumentService = Depends(get_document_service)):
    service.reset_system()
    return {"status": "success", "message": "System reset complete"}
