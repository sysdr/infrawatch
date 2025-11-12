import asyncio
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
from contextlib import asynccontextmanager

from app.routes import metrics, alerts, status
from app.services.stream_manager import StreamManager
from app.services.metric_collector import MetricCollector
from app.services.alert_service import AlertService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Socket.IO
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    ping_timeout=60,
    ping_interval=25,
    compression_threshold=1024
)

stream_manager = StreamManager(sio)
metric_collector = MetricCollector(stream_manager)
alert_service = AlertService(stream_manager, metric_collector)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Real-time Streaming Service...")
    asyncio.create_task(metric_collector.start_collection())
    asyncio.create_task(alert_service.start_monitoring())
    asyncio.create_task(stream_manager.start_throttling())
    yield
    # Shutdown
    logger.info("Shutting down streaming service...")
    await metric_collector.stop()
    await alert_service.stop()
    await stream_manager.stop()

app = FastAPI(title="Real-time Streaming Service", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(metrics.router, prefix="/api/metrics", tags=["metrics"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(status.router, prefix="/api/status", tags=["status"])

# Socket.IO connection handlers
@sio.event
async def connect(sid, environ):
    logger.info(f"Client connected: {sid}")
    await stream_manager.handle_connect(sid)

@sio.event
async def disconnect(sid):
    logger.info(f"Client disconnected: {sid}")
    await stream_manager.handle_disconnect(sid)

@sio.event
async def subscribe(sid, data):
    logger.info(f"Client {sid} subscribing to: {data}")
    await stream_manager.subscribe(sid, data)

@sio.event
async def unsubscribe(sid, data):
    logger.info(f"Client {sid} unsubscribing from: {data}")
    await stream_manager.unsubscribe(sid, data)

@sio.event
async def ping(sid):
    await sio.emit('pong', room=sid)

# Mount Socket.IO
socket_app = socketio.ASGIApp(sio, app)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "active_connections": len(stream_manager.connections),
        "metrics_collected": metric_collector.total_collected
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(socket_app, host="0.0.0.0", port=8000, log_level="info")
