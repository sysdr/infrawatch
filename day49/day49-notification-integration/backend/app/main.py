from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.api import alerts, notifications, preferences, escalations
from app.db.database import engine, Base
from app.core.config import settings
import logging
import asyncio
import re
from sqlalchemy.exc import OperationalError, DatabaseError
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Notification Integration Service", version="1.0.0")

@app.exception_handler(OperationalError)
@app.exception_handler(DatabaseError)
async def database_exception_handler(request: Request, exc: Exception):
    logger.error(f"Database error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "detail": "Database connection failed. Please ensure PostgreSQL is running and credentials are correct.",
            "error": str(exc)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    error_msg = str(exc)
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    if "name resolution" in error_msg.lower() or "temporary failure" in error_msg.lower():
        # Retry logic for DNS issues - return 500 with retry suggestion
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Database connection error. Please retry.",
                "error": "Connection error"
            }
        )
    raise

# CORS - Allow all localhost origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables and verify connection
async def init_db():
    try:
        # Warm up the connection pool
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection pool warmed up")
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        logger.warning("Application will continue but database operations may fail")

@app.on_event("startup")
async def startup_event():
    await init_db()

# Include routers
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(preferences.router, prefix="/api/preferences", tags=["preferences"])
app.include_router(escalations.router, prefix="/api/escalations", tags=["escalations"])

@app.get("/")
def root():
    return {"message": "Notification Integration Service", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}
