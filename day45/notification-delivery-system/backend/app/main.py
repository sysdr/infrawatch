from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any
import logging

from app.api import notifications, delivery, tracking, metrics
from app.core.config import settings
from app.core.database import engine, Base
from app.services.queue_manager import QueueManager
from app.services.delivery_service import DeliveryService
from app.services.websocket_manager import WebSocketManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Notification Delivery System",
    description="High-scale notification delivery with queue management, retry, and tracking",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(delivery.router, prefix="/api/delivery", tags=["delivery"])
app.include_router(tracking.router, prefix="/api/tracking", tags=["tracking"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["metrics"])

# WebSocket manager
websocket_manager = WebSocketManager()

# Global services
queue_manager = None
delivery_service = None

@app.on_event("startup")
async def startup():
    global queue_manager, delivery_service
    logger.info("Starting Notification Delivery System...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Initialize services
    queue_manager = QueueManager()
    delivery_service = DeliveryService(websocket_manager)
    
    # Start background tasks
    asyncio.create_task(queue_manager.start_processing())
    asyncio.create_task(delivery_service.start_delivery_worker())
    
    logger.info("✅ System startup complete")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming websocket messages if needed
            pass
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

@app.get("/")
async def root():
    return {
        "message": "Notification Delivery System",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "queue_manager": queue_manager.is_healthy() if queue_manager else False,
            "delivery_service": delivery_service.is_healthy() if delivery_service else False
        },
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
