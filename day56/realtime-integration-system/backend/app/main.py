from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import structlog
from app.core.config import settings
from app.services.integration_hub import IntegrationHub
from app.websocket.manager import WebSocketManager
from app.api import health, notifications, alerts
from app.core.metrics import MetricsCollector

logger = structlog.get_logger()

# Global managers
integration_hub: IntegrationHub = None
ws_manager: WebSocketManager = None
metrics_collector: MetricsCollector = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global integration_hub, ws_manager, metrics_collector
    
    logger.info("Starting Real-time Integration System...")
    
    # Initialize components
    metrics_collector = MetricsCollector()
    ws_manager = WebSocketManager(metrics_collector)
    integration_hub = IntegrationHub(ws_manager, metrics_collector)
    
    # Start background tasks
    await integration_hub.start()
    
    logger.info("System ready", 
                ws_connections=0,
                circuit_breaker_state="CLOSED")
    
    yield
    
    # Cleanup
    logger.info("Shutting down...")
    await integration_hub.stop()
    await ws_manager.disconnect_all()
    logger.info("Shutdown complete")

app = FastAPI(
    title="Real-time Integration System",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/health", tags=["health"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket connection handler with recovery support"""
    await ws_manager.connect(client_id, websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            await integration_hub.handle_client_message(client_id, data)
    except WebSocketDisconnect:
        logger.info("Client disconnected", client_id=client_id)
    except Exception as e:
        logger.error("WebSocket error", client_id=client_id, error=str(e))
    finally:
        await ws_manager.disconnect(client_id)

@app.get("/")
async def root():
    return {
        "service": "Real-time Integration System",
        "version": "1.0.0",
        "status": "operational",
        "connections": ws_manager.get_connection_count() if ws_manager else 0
    }
