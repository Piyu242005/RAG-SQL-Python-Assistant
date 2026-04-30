"""FastAPI routers for chat endpoints."""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from models import ChatRequest, ChatResponse, Source
from rag_pipeline import RAGPipeline
from limiter import limiter

router = APIRouter(prefix="/api", tags=["chat"])

# Initialize RAG pipeline (singleton)
rag_pipeline = None

def get_rag_pipeline() -> RAGPipeline:
    """Get or initialize RAG pipeline."""
    global rag_pipeline
    if rag_pipeline is None:
        try:
            rag_pipeline = RAGPipeline()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize RAG pipeline: {str(e)}"
            )
    return rag_pipeline

@router.post("/chat", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat(request: ChatRequest, fast_request: Request) -> ChatResponse:
    """
    Process a chat query and return answer with sources.
    
    Args:
        request: ChatRequest with query and optional filters
        
    Returns:
        ChatResponse with answer and source documents
    """
    try:
        pipeline = get_rag_pipeline()
        
        # Query with optional filter
        if request.doc_type:
            if request.doc_type not in ['mysql', 'python']:
                raise HTTPException(
                    status_code=400,
                    detail="doc_type must be 'mysql' or 'python'"
                )
            result = pipeline.query_with_filter(request.query, request.doc_type)
        else:
            result = pipeline.query(request.query)
        
        # Convert sources to Pydantic models
        sources = [Source(**source) for source in result['sources']]
        
        return ChatResponse(
            answer=result['answer'],
            sources=sources,
            success=result['success'],
            error=result.get('error'),
            filter_applied=result.get('filter_applied')
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

@router.post("/chat/stream")
@limiter.limit("5/minute")
async def chat_stream(request: ChatRequest, fast_request: Request):
    """
    Stream a chat response.
    """
    try:
        pipeline = get_rag_pipeline()
        
        async def event_generator():
            # Use conversation_id as session_id for Redis memory
            session_id = request.conversation_id or "default"
            async for chunk in pipeline.stream_query(request.query, request.doc_type, session_id=session_id):
                yield chunk

        return StreamingResponse(event_generator(), media_type="text/event-stream")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
