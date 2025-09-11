from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import uvicorn
from typing import List
from .api import tasks, monitoring, workers
from .services.monitoring_service import MonitoringService
from .services.websocket_manager import WebSocketManager

app = FastAPI(title="Task Monitoring System", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Global services
monitoring_service = MonitoringService()
websocket_manager = WebSocketManager()

# Include routers
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["monitoring"])
app.include_router(workers.router, prefix="/api/workers", tags=["workers"])

@app.websocket("/ws/monitoring")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Send real-time monitoring data
            metrics = await monitoring_service.get_realtime_metrics()
            await websocket_manager.send_personal_message(json.dumps(metrics), websocket)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

@app.on_event("startup")
async def startup_event():
    await monitoring_service.initialize()
    asyncio.create_task(monitoring_service.start_background_monitoring())

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
