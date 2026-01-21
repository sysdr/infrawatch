from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging
from app.core.config import settings
from app.routers import k8s_router, health_router, metrics_router
from app.services.k8s_monitor import K8sMonitorService
from app.services.websocket_manager import WebSocketManager
from app.core.database import init_db

logger = logging.getLogger(__name__)

# Global instances
k8s_monitor = None
ws_manager = WebSocketManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global k8s_monitor
    print("Initializing database...")
    await init_db()
    
    print("Starting Kubernetes monitoring service...")
    k8s_monitor = K8sMonitorService(ws_manager)
    asyncio.create_task(k8s_monitor.start_monitoring())
    
    yield
    
    # Shutdown
    print("Stopping Kubernetes monitoring...")
    if k8s_monitor:
        await k8s_monitor.stop_monitoring()

app = FastAPI(
    title="Kubernetes Monitoring System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(k8s_router.router, prefix="/api/v1/k8s", tags=["kubernetes"])
app.include_router(health_router.router, prefix="/api/v1/health", tags=["health"])
app.include_router(metrics_router.router, prefix="/api/v1/metrics", tags=["metrics"])

@app.websocket("/ws/updates")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        # Send a welcome message
        await websocket.send_json({"type": "connected", "message": "WebSocket connection established"})
        
        # Keep connection alive by waiting for messages or sending periodic pings
        while True:
            try:
                # Wait for client messages or timeout
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                # Echo back if needed (optional)
                # await websocket.send_text(f"Echo: {data}")
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                try:
                    await websocket.send_json({"type": "ping", "timestamp": asyncio.get_event_loop().time()})
                except Exception as e:
                    logger.error(f"Error sending ping: {e}")
                    break
            except WebSocketDisconnect:
                break
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        ws_manager.disconnect(websocket)

@app.get("/")
async def root():
    return {
        "service": "Kubernetes Monitoring System",
        "version": "1.0.0",
        "status": "operational"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
