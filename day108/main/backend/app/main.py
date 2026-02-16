from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.metric import Base
from app.api.metrics import router as metrics_router
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://metrics_user:metrics_pass@localhost:5432/metrics_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(title="Custom Metrics Engine", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(metrics_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "custom-metrics-engine"}

@app.get("/")
async def root():
    return {
        "message": "Custom Metrics Engine API",
        "version": "1.0.0",
        "endpoints": {
            "metrics": "/api/metrics/definitions",
            "calculate": "/api/metrics/calculate/{metric_id}",
            "validate": "/api/metrics/validate-formula",
            "performance": "/api/metrics/performance/{metric_id}"
        }
    }
