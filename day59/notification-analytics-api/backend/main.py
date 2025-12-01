from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from database.db_config import init_db
from api import chart_router, aggregation_router, trend_router, comparison_router
from jobs import start_aggregation_jobs
import logging
import traceback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing database...")
    await init_db()
    logger.info("Starting background jobs...")
    # start_aggregation_jobs()  # Uncomment for production
    yield
    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(
    title="Notification Analytics API",
    description="Data visualization and analytics API for notification systems",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(chart_router)
app.include_router(aggregation_router)
app.include_router(trend_router)
app.include_router(comparison_router)

@app.get("/")
async def root():
    return {
        "message": "Notification Analytics API",
        "version": "1.0.0",
        "endpoints": {
            "charts": "/api/analytics/chart",
            "trends": "/api/analytics/trends",
            "compare": "/api/analytics/compare",
            "drilldown": "/api/analytics/drilldown"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler that includes CORS headers"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "type": type(exc).__name__
        },
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
