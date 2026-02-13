from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys

from .database import init_db
from .config import settings
from .api.pipeline_routes import router as ml_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ML Pipeline API — Day 106",
    description="Machine Learning Pipeline for Infrastructure Management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(ml_router)

@app.on_event("startup")
async def startup():
    await init_db()
    logger.info("Database initialized")

@app.get("/api/v1/health")
async def health():
    return {"status": "healthy", "service": "ml-pipeline", "version": "1.0.0"}

@app.get("/")
async def root():
    return {"message": "Day 106 ML Pipeline API", "docs": "/docs"}
