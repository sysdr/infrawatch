from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import asyncio
import json
from .api.metrics import router as metrics_router
from .websocket.manager import manager, generate_sample_metrics
from .models.metrics import get_db, MetricData
from config.settings import settings

app = FastAPI(title=settings.app_name)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(metrics_router, prefix="/api/v1")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "subscribe":
                await manager.subscribe_metric(websocket, message["metric_name"])
            elif message["type"] == "unsubscribe":
                await manager.unsubscribe_metric(websocket, message["metric_name"])
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.on_event("startup")
async def startup_event():
    # Start generating sample metrics
    asyncio.create_task(generate_sample_metrics())

@app.get("/")
async def root():
    return {"message": "Metrics Dashboard API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
