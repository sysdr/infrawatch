from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import structlog
from contextlib import asynccontextmanager

from config.database import init_db, close_redis
from app.controllers.metrics_controller import router as metrics_router

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Metrics API server...")
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    await close_redis()

app = FastAPI(
    title="Metrics API",
    description="Production-ready metrics collection and query API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(metrics_router)

@app.get("/")
async def root():
    return {
        "message": "Metrics API v1.0.0",
        "status": "operational",
        "docs": "/docs"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error("Unhandled exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
