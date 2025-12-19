from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from datetime import datetime
import json
import socketio

from app.core.redis_client import redis_client
from app.api import dashboard, metrics, cache
from app.services.data_generator import DataGenerator

# Create Socket.IO server
sio = socketio.AsyncServer(
    cors_allowed_origins=["http://localhost:3000"],
    async_mode='asgi',
    logger=True,
    engineio_logger=True
)
data_generator = DataGenerator()

# Initialize startup tasks
async def startup():
    await redis_client.connect()
    asyncio.create_task(simulate_metrics_updates())
    print("Backend startup complete - Redis connected, metrics simulation started")

async def shutdown():
    await redis_client.disconnect()
    print("Backend shutdown complete - Redis disconnected")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await startup()
    yield
    # Shutdown
    await shutdown()

fastapi_app = FastAPI(title="Dashboard Performance API", lifespan=lifespan)

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fastapi_app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
fastapi_app.include_router(metrics.router, prefix="/api/metrics", tags=["metrics"])
fastapi_app.include_router(cache.router, prefix="/api/cache", tags=["cache"])

@fastapi_app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "redis": await redis_client.ping()
    }

@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

@sio.event
async def message(sid, data):
    # Handle client messages if needed
    await sio.emit('message', {"type": "pong"}, room=sid)

async def simulate_metrics_updates():
    """Simulate real-time metric updates"""
    await asyncio.sleep(5)  # Wait for startup
    
    while True:
        try:
            # Generate random metric updates
            updates = data_generator.generate_metric_updates(count=50)
            
            # Broadcast to all connected clients via Socket.IO
            await sio.emit('message', {
                "type": "metrics_update",
                "data": updates,
                "timestamp": datetime.now().isoformat()
            })
            
            await asyncio.sleep(1.0)  # 1 update per second
        except Exception as e:
            print(f"Error in metrics updates: {e}")
            await asyncio.sleep(5)

# Mount Socket.IO app - this becomes the main app for uvicorn
# socketio_path is where Socket.IO mounts its Engine.IO server
# The client should use the same path in its configuration
app = socketio.ASGIApp(
    sio, 
    fastapi_app, 
    socketio_path='/ws/metrics',
    on_startup=startup,
    on_shutdown=shutdown
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
