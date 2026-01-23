from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

from app.api.routes import discovery, inventory, topology, changes
from app.services.discovery_engine import DiscoveryEngine
from app.services.change_detector import ChangeDetector
from app.utils.database import init_db
from app.utils.websocket_manager import manager

# Global instances
discovery_engine = None
change_detector = None
discovery_task = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global discovery_engine, change_detector, discovery_task
    
    # Startup
    await init_db()
    discovery_engine = DiscoveryEngine()
    change_detector = ChangeDetector()
    
    # Start background discovery
    discovery_task = asyncio.create_task(run_discovery())
    
    yield
    
    # Shutdown
    if discovery_task:
        discovery_task.cancel()

async def run_discovery():
    """Background task for continuous discovery"""
    global discovery_engine, change_detector
    
    while True:
        try:
            # Run discovery
            resources = await discovery_engine.discover_all()
            
            # Detect changes
            changes = await change_detector.detect_changes(resources)
            
            # Notify via WebSocket
            if changes:
                await manager.broadcast({
                    "type": "changes_detected",
                    "count": len(changes),
                    "changes": changes[:10]  # Send first 10
                })
            
            await asyncio.sleep(30)  # Discovery cycle every 30 seconds
        except Exception as e:
            print(f"Discovery error: {e}")
            await asyncio.sleep(60)

app = FastAPI(
    title="Infrastructure Discovery System",
    description="Auto-discover, inventory, and map cloud infrastructure",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(discovery.router, prefix="/api/discovery", tags=["discovery"])
app.include_router(inventory.router, prefix="/api/inventory", tags=["inventory"])
app.include_router(topology.router, prefix="/api/topology", tags=["topology"])
app.include_router(changes.router, prefix="/api/changes", tags=["changes"])

@app.get("/")
async def root():
    return {
        "message": "Infrastructure Discovery System API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}
