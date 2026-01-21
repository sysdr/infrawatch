from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from ..api.routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="Container Monitoring API",
    description="Real-time Docker container monitoring system",
    version="1.0.0"
)

# CORS middleware - allow all localhost ports for development
import os
import re

# In development, dynamically allow any localhost origin
# This handles any port the frontend might use
is_development = os.getenv("ENVIRONMENT", "development") == "development"

if is_development:
    # Development: Use a custom approach to allow any localhost origin
    # We'll manually handle CORS in a middleware to support any localhost port
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.requests import Request
    from starlette.responses import Response
    
    class DevelopmentCORSMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            origin = request.headers.get("origin")
            referer = request.headers.get("referer", "")
            
            # Determine origin from referer if origin header is missing (proxy requests)
            if not origin and referer:
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(referer)
                    origin = f"{parsed.scheme}://{parsed.netloc}"
                except:
                    pass
            
            # Handle preflight OPTIONS requests
            if request.method == "OPTIONS":
                if origin and self._is_localhost(origin):
                    return Response(
                        status_code=200,
                        headers={
                            "Access-Control-Allow-Origin": origin,
                            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                            "Access-Control-Allow-Headers": "*",
                            "Access-Control-Allow-Credentials": "true",
                            "Access-Control-Max-Age": "3600",
                        }
                    )
                # Allow OPTIONS even without origin (for proxy requests)
                return Response(
                    status_code=200,
                    headers={
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                        "Access-Control-Allow-Headers": "*",
                    }
                )
            
            # Handle actual requests
            response = await call_next(request)
            
            # Add CORS headers for localhost origins
            if origin and self._is_localhost(origin):
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Methods"] = "*"
                response.headers["Access-Control-Allow-Headers"] = "*"
                response.headers["Access-Control-Expose-Headers"] = "*"
                response.headers["Access-Control-Allow-Credentials"] = "true"
            elif not origin:
                # If no origin (direct request or proxy), allow it
                response.headers["Access-Control-Allow-Origin"] = "*"
            
            return response
        
        def _is_localhost(self, origin: str) -> bool:
            """Check if origin is localhost or 127.0.0.1"""
            if not origin:
                return False
            return (origin.startswith("http://localhost:") or 
                    origin.startswith("http://127.0.0.1:") or
                    origin.startswith("https://localhost:") or
                    origin.startswith("https://127.0.0.1:"))
    
    app.add_middleware(DevelopmentCORSMiddleware)
else:
    # Production: specific origins only
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:3002",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
            "http://127.0.0.1:3002",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

# Include routers
app.include_router(router, prefix="/api/v1", tags=["monitoring"])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "container-monitoring"}


@app.on_event("startup")
async def startup_event():
    logging.info("Container Monitoring API started")


@app.on_event("shutdown")
async def shutdown_event():
    logging.info("Container Monitoring API shutting down")
