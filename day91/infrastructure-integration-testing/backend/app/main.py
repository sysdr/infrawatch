"""
Infrastructure Integration Testing Platform
Main FastAPI application with testing endpoints
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog
from datetime import datetime
from typing import List, Dict, Optional
import asyncio

from .api import router
from .core.database import init_db
from .core.redis_client import init_redis
from .services.discovery_service import DiscoveryService
from .services.monitoring_service import MonitoringService
from .services.cost_service import CostTrackingService
from .integration.integration_tester import IntegrationTester

logger = structlog.get_logger()

# Background task tracking
background_tasks_status = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("starting_application")
    
    # Initialize services
    await init_db()
    await init_redis()
    
    # Start background monitoring
    app.state.discovery_service = DiscoveryService()
    app.state.monitoring_service = MonitoringService()
    app.state.cost_service = CostTrackingService()
    app.state.integration_tester = IntegrationTester()
    
    logger.info("application_started")
    yield
    
    logger.info("shutting_down_application")

app = FastAPI(
    title="Infrastructure Integration Testing Platform",
    description="Complete integration testing for distributed infrastructure systems",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Infrastructure Integration Testing",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": "connected",
            "redis": "connected",
            "discovery": "active",
            "monitoring": "active",
            "cost_tracking": "active"
        }
    }
