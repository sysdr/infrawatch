from fastapi import FastAPI, WebSocket, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from typing import List, Optional
from datetime import datetime, timedelta
import json

from api.logs import router as logs_router
from api.alerts import router as alerts_router
from utils.redis_client import get_redis_client
from utils.elasticsearch_client import get_es_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Log Integration Service...")
    yield
    # Shutdown
    print("🛑 Shutting down Log Integration Service...")

app = FastAPI(
    title="Log Management Integration",
    description="Production-grade log pipeline with hot/warm/cold paths",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(logs_router, prefix="/api/logs", tags=["logs"])
app.include_router(alerts_router, prefix="/api/alerts", tags=["alerts"])

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "log-integration"
    }

@app.get("/metrics")
async def metrics():
    """Prometheus-compatible metrics"""
    redis = await get_redis_client()
    es = await get_es_client()

    metrics_data = {
        "websocket_connections": await redis.get("metrics:websocket:connections") or 0,
        "logs_ingested_total": await redis.get("metrics:logs:ingested") or 0,
        "logs_indexed_total": await redis.get("metrics:logs:indexed") or 0,
        "alerts_triggered_total": await redis.get("metrics:alerts:triggered") or 0,
    }

    return metrics_data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
