from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
import uuid
# Models imported by services, not needed directly here
from services.service_container import notification_service, websocket_manager
from api import notification_routes, preference_routes, history_routes, test_routes

app = FastAPI(title="Notification UI System", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(notification_routes.router, prefix="/api/notifications")
app.include_router(preference_routes.router, prefix="/api/preferences")
app.include_router(history_routes.router, prefix="/api/history")
app.include_router(test_routes.router, prefix="/api/test")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "subscribe":
                websocket_manager.subscribe_user(websocket, message.get("userId"))
            elif message.get("type") == "acknowledge":
                await notification_service.acknowledge_notification(
                    message.get("notificationId")
                )
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

@app.on_event("startup")
async def startup_event():
    """Initialize notification system on startup"""
    await notification_service.initialize()
    # Start background task for processing notifications
    asyncio.create_task(notification_background_processor())

async def notification_background_processor():
    """Background task to process and send notifications"""
    while True:
        try:
            # Simulate receiving notifications from external services
            await asyncio.sleep(5)
            
            # Generate sample notification for demo using the service
            notification_data = {
                "title": "System Alert",
                "message": f"Sample notification at {datetime.now().strftime('%H:%M:%S')}",
                "type": "info",
                "priority": "medium",
                "userId": "demo-user"
            }
            
            # Create notification through service (this stores it and creates history)
            notification = await notification_service.create_notification(notification_data)
            
            # Add history entry for sending
            await notification_service.add_history_entry(
                notification.id, "sent", {"channel": "websocket", "timestamp": datetime.now().isoformat()}
            )
            
            # Convert to dict for broadcasting
            notification_dict = {
                "id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "type": notification.type.value,
                "timestamp": notification.timestamp.isoformat(),
                "priority": notification.priority.value,
                "userId": notification.userId,
                "acknowledged": notification.acknowledged,
                "data": notification.data
            }
            
            # Broadcast to connected clients
            await websocket_manager.broadcast_notification(notification_dict)
            
        except Exception as e:
            print(f"Error in background processor: {e}")
            await asyncio.sleep(1)

@app.get("/")
async def root():
    return {"message": "Notification UI System API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
