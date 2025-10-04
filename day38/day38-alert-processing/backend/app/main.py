from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any
from .services.alert_processor import AlertProcessor
from .services.websocket_manager import WebSocketManager
from .api.alert_routes import router as alert_router
from .models.database import init_db

app = FastAPI(title="Alert Processing Pipeline", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
websocket_manager = WebSocketManager()
alert_processor = AlertProcessor(websocket_manager)

# Include API routes
app.include_router(alert_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    await init_db()
    await alert_processor.start()
    print("🚨 Alert Processing Pipeline started")

@app.on_event("shutdown")
async def shutdown_event():
    await alert_processor.stop()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print(f"🔌 WebSocket connection attempt from {websocket.client}")
    await websocket_manager.connect(websocket)
    print(f"✅ WebSocket connected. Total connections: {websocket_manager.connection_count()}")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        print(f"🔌 WebSocket disconnected from {websocket.client}")
        websocket_manager.disconnect(websocket)

@app.get("/")
async def root():
    return {"message": "Alert Processing Pipeline API", "status": "active"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "alert_processor": alert_processor.is_running(),
            "websocket_manager": websocket_manager.connection_count()
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
