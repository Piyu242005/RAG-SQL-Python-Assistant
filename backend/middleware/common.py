import time
import uuid
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("api-middleware")

class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add a unique request ID to every request."""
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

class LoggingMiddleware(BaseHTTPMiddleware):
    """Structured logging for every request."""
    async def dispatch(self, request: Request, call_next):
        logger.info(f"Incoming request: {request.method} {request.url.path}")
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")
        return response
