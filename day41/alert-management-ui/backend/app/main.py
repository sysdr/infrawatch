from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import asyncio
import json
from typing import List
import logging
from datetime import datetime, timedelta
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Alert Management API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection: {len(self.active_connections)} active")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected: {len(self.active_connections)} active")

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

# Import shared data
from data import sample_alerts, alert_rules

# Import routes
from routes import alerts, rules
app.include_router(alerts.router)
app.include_router(rules.router)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial data
        await websocket.send_text(json.dumps({
            "type": "initial_data",
            "alerts": sample_alerts[:10]
        }))
        
        # Keep connection alive and send periodic updates
        while True:
            await asyncio.sleep(10)  # Send updates every 10 seconds
            
            # Simulate new alert
            new_alert = {
                "id": f"alert_{random.randint(1000, 9999)}",
                "title": f"New Alert - Server {random.randint(1, 5)}",
                "severity": random.choice(["critical", "warning", "info"]),
                "status": "active",
                "timestamp": datetime.now().isoformat(),
                "description": "Automated alert triggered",
                "source": f"server-{random.randint(1, 5)}",
                "tags": ["infrastructure", "automated"],
                "assignee": None,
                "rule_id": f"rule_{random.randint(1, 5)}",
                "metric_value": random.randint(80, 100),
                "threshold": 85
            }
            
            await websocket.send_text(json.dumps({
                "type": "new_alert",
                "alert": new_alert
            }))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/")
async def root():
    return {"message": "Alert Management API", "version": "1.0.0"}

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
