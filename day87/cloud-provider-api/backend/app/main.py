from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from app.core.config import settings
from app.api import resources, costs, health, autoscaling
from app.services.collector_manager import CollectorManager

collector_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global collector_manager
    collector_manager = CollectorManager()
    
    # Start background collection tasks
    asyncio.create_task(collector_manager.start_collection())
    
    yield
    
    # Shutdown
    await collector_manager.stop_collection()

app = FastAPI(
    title="Cloud Infrastructure Management API",
    description="Production-grade cloud provider integration",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(resources.router, prefix="/api/v1/resources", tags=["resources"])
app.include_router(costs.router, prefix="/api/v1/costs", tags=["costs"])
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
app.include_router(autoscaling.router, prefix="/api/v1/autoscaling", tags=["autoscaling"])

@app.get("/")
async def root():
    return {
        "service": "Cloud Provider API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/api/v1/status")
async def get_status():
    return {
        "collector_status": collector_manager.get_status() if collector_manager else {},
        "cache_stats": await collector_manager.get_cache_stats() if collector_manager else {}
    }
