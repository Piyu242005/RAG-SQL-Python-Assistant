from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from services.chat_service import ChatService
import json
import logging

router = APIRouter(tags=["Chat"])
chat_service = ChatService()

class ChatRequest(BaseModel):
    question: str
    session_id: str = "default"

@router.post("/chat/stream")
async def stream_chat(payload: ChatRequest):
    async def generator():
        try:
            async for chunk in chat_service.stream(payload.question, payload.session_id):
                # Format for SSE
                yield f"data: {json.dumps({'text': chunk})}\n\n"
        except Exception as e:
            logging.error(f"Error in stream_chat: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(generator(), media_type="text/event-stream")
