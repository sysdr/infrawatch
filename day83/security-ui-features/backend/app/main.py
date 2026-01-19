from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio
from typing import List, Dict, Any
import json
from datetime import datetime, timedelta
import random
import traceback

from app.core.database import engine, Base, get_db
from app.core.redis_client import get_redis_client
from app.websockets.security_stream import SecurityWebSocketManager
from app.api import security_events, security_metrics, security_settings, audit_logs, security_reports
from app.services.event_generator import SecurityEventGenerator

# WebSocket manager instance
ws_manager = SecurityWebSocketManager()
event_generator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Warning: Could not create database tables: {e}")
        print("The application will continue but database features may not work.")
    
    # Start event generator
    global event_generator
    event_generator = SecurityEventGenerator(ws_manager)
    asyncio.create_task(event_generator.generate_events())
    
    yield
    
    # Shutdown
    if event_generator:
        event_generator.stop()
    await ws_manager.disconnect_all()

app = FastAPI(
    title="Security UI Features API",
    description="Real-time security monitoring and management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration - Must be added before routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Exception handler to ensure CORS headers are always included
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Ensure CORS headers are included even in error responses"""
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "type": type(exc).__name__
        },
        headers={
            "Access-Control-Allow-Origin": request.headers.get("origin", "http://localhost:3000"),
            "Access-Control-Allow-Credentials": "true",
        }
    )

# Include routers
app.include_router(security_events.router, prefix="/api/security/events", tags=["Security Events"])
app.include_router(security_metrics.router, prefix="/api/security/metrics", tags=["Security Metrics"])
app.include_router(security_settings.router, prefix="/api/security/settings", tags=["Security Settings"])
app.include_router(audit_logs.router, prefix="/api/security/audit", tags=["Audit Logs"])
app.include_router(security_reports.router, prefix="/api/security/reports", tags=["Security Reports"])

@app.websocket("/ws/security/events")
async def websocket_security_events(websocket: WebSocket):
    await ws_manager.connect(websocket)
    client_info = f"{websocket.client.host if websocket.client else 'unknown'}:{websocket.client.port if websocket.client else 'unknown'}"
    print(f"WebSocket connected from {client_info}")
    
    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connected",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "WebSocket connected successfully"
        })
        print(f"WebSocket initial message sent to {client_info}")
        
        # Keep connection alive by handling both incoming messages and keepalive
        while True:
            try:
                # Wait for message with timeout to keep connection alive
                # Use a shorter timeout to detect disconnections faster
                data = await asyncio.wait_for(websocket.receive_text(), timeout=60.0)
                
                try:
                    message = json.loads(data)
                    
                    if message.get("type") == "ping":
                        await websocket.send_json({"type": "pong", "timestamp": datetime.utcnow().isoformat()})
                    elif message.get("type") == "subscribe":
                        # Handle subscription to specific event types
                        await ws_manager.subscribe_filters(websocket, message.get("filters", {}))
                        await websocket.send_json({
                            "type": "subscribed",
                            "filters": message.get("filters", {}),
                            "timestamp": datetime.utcnow().isoformat()
                        })
                    else:
                        print(f"WebSocket received unknown message type: {message.get('type')}")
                except json.JSONDecodeError as e:
                    print(f"WebSocket JSON decode error: {e}, data: {data[:100]}")
                    # Invalid JSON, ignore but keep connection alive
                    continue
                    
            except asyncio.TimeoutError:
                # Send keepalive ping to keep connection alive
                try:
                    await websocket.send_json({
                        "type": "keepalive",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                except WebSocketDisconnect:
                    print(f"WebSocket disconnected during keepalive (normal)")
                    break
                except Exception as e:
                    # Connection closed, break from loop
                    print(f"WebSocket keepalive failed: {type(e).__name__}: {e}")
                    break
            except WebSocketDisconnect:
                # Client disconnected normally
                print(f"WebSocket disconnected normally from {client_info}")
                break
            except Exception as e:
                # Log error but try to keep connection alive for other errors
                print(f"WebSocket message handling error: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                # Don't break on minor errors, just continue
                continue
                
    except WebSocketDisconnect:
        # Normal disconnection
        print(f"WebSocket disconnected from {client_info}")
    except Exception as e:
        print(f"WebSocket outer error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Always disconnect when exiting
        print(f"WebSocket cleanup for {client_info}")
        ws_manager.disconnect(websocket)

@app.get("/")
async def root():
    return {
        "service": "Security UI Features API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "events": "/api/security/events",
            "metrics": "/api/security/metrics",
            "settings": "/api/security/settings",
            "audit": "/api/security/audit",
            "reports": "/api/security/reports",
            "websocket": "/ws/security/events"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "active_connections": ws_manager.get_connection_count()
    }
