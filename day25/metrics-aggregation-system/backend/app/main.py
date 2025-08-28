from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import asyncio
import json
import logging
from datetime import datetime
from typing import List, Dict, Any
import uvicorn

from .aggregation.engine import AggregationEngine
from .aggregation.rollup import RollupManager
from .aggregation.statistics import StatisticalCalculator
from .api.routes import router as api_router
from .models.metrics import MetricData, AggregatedMetric
from .storage.timeseries import TimeSeriesStorage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Metrics Aggregation System", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
aggregation_engine = AggregationEngine()
rollup_manager = RollupManager()
stats_calculator = StatisticalCalculator()
storage = TimeSeriesStorage()

# WebSocket connections manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        if self.active_connections:
            disconnected = []
            for connection in self.active_connections:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    disconnected.append(connection)
            
            for conn in disconnected:
                self.disconnect(conn)

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Metrics Aggregation System...")
    
    # Initialize storage
    await storage.initialize()
    
    # Start background tasks
    asyncio.create_task(generate_sample_metrics())
    asyncio.create_task(background_aggregation())
    asyncio.create_task(rollup_scheduler())
    
    logger.info("System initialized successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Metrics Aggregation System...")
    await storage.close()

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/")
async def root():
    return {"message": "Metrics Aggregation System", "status": "running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "aggregation_engine": "running",
            "rollup_manager": "running",
            "storage": "connected"
        }
    }

async def generate_sample_metrics():
    """Generate sample metrics for demonstration"""
    import random
    import asyncio
    
    metric_types = ["cpu_usage", "memory_usage", "request_count", "response_time", "error_rate"]
    
    while True:
        try:
            # Generate random metrics
            for metric_type in metric_types:
                for server in ["server-1", "server-2", "server-3"]:
                    value = random.uniform(10, 90) if "usage" in metric_type else random.uniform(0, 100)
                    
                    metric = MetricData(
                        name=metric_type,
                        value=value,
                        timestamp=datetime.utcnow(),
                        tags={"server": server, "environment": "demo"}
                    )
                    
                    # Process metric through aggregation
                    await aggregation_engine.process_metric(metric)
                    
                    # Store raw metric
                    await storage.store_metric(metric)
            
            await asyncio.sleep(1)  # Generate metrics every second
            
        except Exception as e:
            logger.error(f"Error generating sample metrics: {e}")
            await asyncio.sleep(5)

async def background_aggregation():
    """Background task for real-time aggregation"""
    while True:
        try:
            # Get aggregated metrics
            aggregated = await aggregation_engine.get_current_aggregations()
            
            # Broadcast to WebSocket clients
            if aggregated:
                await manager.broadcast({
                    "type": "aggregated_metrics",
                    "data": aggregated,
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            await asyncio.sleep(5)  # Send updates every 5 seconds
            
        except Exception as e:
            logger.error(f"Error in background aggregation: {e}")
            await asyncio.sleep(10)

async def rollup_scheduler():
    """Schedule rollup operations"""
    while True:
        try:
            # Perform rollups every minute
            await rollup_manager.perform_rollups()
            await asyncio.sleep(60)
            
        except Exception as e:
            logger.error(f"Error in rollup scheduler: {e}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
