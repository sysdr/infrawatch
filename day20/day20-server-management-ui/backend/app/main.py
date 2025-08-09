from fastapi import FastAPI, WebSocket, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import asyncio
import json
from typing import List, Dict, Optional
from datetime import datetime
import uuid

from .models import Server, ServerCreate, ServerUpdate, BulkAction
from .services import ServerService, websocket_manager
from .routes import servers

app = FastAPI(title="Server Management API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
server_service = ServerService()

# Include routers
app.include_router(servers.router, prefix="/api/servers", tags=["servers"])

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    await server_service.initialize()
    # Start background task for server status monitoring
    asyncio.create_task(monitor_server_status())

async def monitor_server_status():
    """Background task to monitor server status and send WebSocket updates"""
    while True:
        try:
            servers = await server_service.get_all_servers()
            for server in servers:
                # Simulate status check
                old_status = server.status
                new_status = await server_service.check_server_status(server.id)
                
                if old_status != new_status:
                    await websocket_manager.broadcast({
                        "type": "status_update",
                        "server_id": server.id,
                        "old_status": old_status,
                        "new_status": new_status,
                        "timestamp": datetime.now().isoformat()
                    })
            
            await asyncio.sleep(30)  # Check every 30 seconds
        except Exception as e:
            print(f"Error in status monitoring: {e}")
            await asyncio.sleep(60)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "subscribe":
                await websocket_manager.add_to_room(websocket, message.get("room", "default"))
            elif message.get("type") == "heartbeat":
                await websocket.send_text(json.dumps({"type": "pong"}))
                
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        websocket_manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
