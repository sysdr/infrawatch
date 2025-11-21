import os
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .utils.db_pool import db_pool
from .utils.redis_queue import redis_queue
from .utils.memory_monitor import memory_monitor
from .services.connection_manager import manager
from .services.notification_service import notification_service
from .services.metrics_collector import metrics_collector
from .models.notification import NotificationCreate, Notification, ConnectionMetrics
from .routers import notifications, websocket, metrics

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting application...")
    
    # Initialize database pool
    await db_pool.create_pool()
    
    # Initialize Redis
    await redis_queue.connect()
    
    # Create tables
    async with db_pool.get_connection() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(100) NOT NULL,
                message TEXT NOT NULL,
                priority VARCHAR(20) DEFAULT 'normal',
                notification_type VARCHAR(50) DEFAULT 'info',
                created_at TIMESTAMP NOT NULL,
                delivered BOOLEAN DEFAULT FALSE,
                delivered_at TIMESTAMP
            )
        """)
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON notifications(user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_delivered ON notifications(delivered)")
    
    # Start background services
    await memory_monitor.start_monitoring()
    asyncio.create_task(notification_service.start_worker())
    asyncio.create_task(manager.start_batch_flusher())
    await metrics_collector.start_collection()
    
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await notification_service.stop_worker()
    await metrics_collector.stop_collection()
    await memory_monitor.stop_monitoring()
    await redis_queue.disconnect()
    await db_pool.close_pool()
    logger.info("Application shut down complete")

app = FastAPI(
    title="Real-time Performance System",
    description="High-performance WebSocket notification system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["metrics"])

@app.get("/")
async def root():
    return {
        "message": "Real-time Performance System API",
        "version": "1.0.0",
        "active_connections": manager.get_connection_count()
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "connections": manager.get_connection_count(),
        "memory_mb": memory_monitor.get_current_memory()
    }
