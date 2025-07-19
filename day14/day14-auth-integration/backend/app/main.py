from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
import uvicorn
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.core.config import settings
from app.middleware.auth_middleware import AuthMiddleware

app = FastAPI(
    title="Authentication Integration API",
    description="Day 14: Complete authentication system with token management",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom auth middleware
app.add_middleware(AuthMiddleware)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users_router, prefix="/api/users", tags=["Users"])

@app.get("/")
async def root():
    return {
        "message": "Authentication Integration API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "auth-integration"}

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code,
            "timestamp": str(request.state.timestamp) if hasattr(request.state, 'timestamp') else None
        }
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
