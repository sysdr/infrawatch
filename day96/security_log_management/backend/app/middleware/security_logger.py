from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import uuid
from datetime import datetime

class SecurityLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate correlation ID
        correlation_id = str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        request.state.start_time = datetime.utcnow()
        
        # Add correlation ID to response headers
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        
        return response
