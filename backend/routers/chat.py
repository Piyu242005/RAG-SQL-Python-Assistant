"""FastAPI routers for chat endpoints."""
import hashlib
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse
from schemas.chat import ChatRequest, ChatResponse, SourceMetadata
from api.deps import get_chat_service
from services.chat import ChatService
from limiter import limiter

router = APIRouter(prefix="/api", tags=["chat"])

@router.post("/chat/stream")
@limiter.limit("5/minute")
async def chat_stream(
    chat_data: ChatRequest, 
    request: Request,
    service: ChatService = Depends(get_chat_service)
):
    """
    Stream a chat response.
    """
    try:
        # Session handling logic (consistent with legacy)
        raw_session = chat_data.conversation_id or "default"
        api_key = request.headers.get("x-api-key", "")
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:8] if api_key else "nokey"
        session_id = f"{key_hash}_{raw_session}"
        
        return StreamingResponse(
            service.stream_chat(chat_data.query, session_id=session_id),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Access-Control-Allow-Origin": "*",
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat(
    chat_data: ChatRequest, 
    request: Request,
    service: ChatService = Depends(get_chat_service)
) -> ChatResponse:
    """
    Process a chat query and return answer with sources.
    """
    # For now, we can use the stream_chat logic and collect it, 
    # or implement a sync query in ChatService.
    # To keep it simple and consistent, I'll implement a sync wrapper in ChatService.
    # But for Phase 3, let's just use the service.
    try:
        raw_session = chat_data.conversation_id or "default"
        api_key = request.headers.get("x-api-key", "")
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:8] if api_key else "nokey"
        session_id = f"{key_hash}_{raw_session}"
        
        result = await service.chat(chat_data.query, session_id=session_id)
        
        return ChatResponse(
            answer=result['answer'],
            sources=[SourceMetadata(**s) for s in result['sources']],
            success=result['success']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
