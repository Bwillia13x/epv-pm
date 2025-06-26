"""
API middleware for error handling and request ID generation
"""
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import uuid
import logging

logger = logging.getLogger(__name__)

from starlette.middleware.base import BaseHTTPMiddleware

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            request_id = request.state.request_id if hasattr(request.state, 'request_id') else 'N/A'
            logger.error(f"Request {request_id} failed: {e}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal Server Error", "request_id": request_id}
            )
