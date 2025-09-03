from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog
from app.api.metrics import router as metrics_router
from app.services.database import db_service
from app.services.redis_service import redis_service

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
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
    logger.info("Starting Metrics System Integration API")
    
    # Initialize services
    try:
        await redis_service.connect()
        logger.info("Redis service connected successfully")
    except Exception as e:
        logger.error("Redis connection failed", error=str(e))
        logger.warning("Application will continue without Redis")
    
    try:
        await db_service.create_tables()
        logger.info("Database service initialized successfully")
    except Exception as e:
        logger.error("Database initialization failed", error=str(e))
        logger.warning("Application will continue without database")
    
    logger.info("Services initialization completed")
    
    yield
    
    # Shutdown
    logger.info("Shutting down services")
    try:
        await redis_service.disconnect()
    except Exception as e:
        logger.error("Redis disconnect failed", error=str(e))

app = FastAPI(
    title="Metrics System Integration API",
    description="Day 28: Metrics collection with storage integration and real-time updates",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(metrics_router, prefix="/api/v1", tags=["metrics"])

@app.get("/")
async def root():
    return {"message": "Metrics System Integration API", "version": "1.0.0", "day": 28}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
