from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
import logging

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Add timestamp to request state
        request.state.timestamp = int(time.time())
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error", "timestamp": request.state.timestamp}
            )
