from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import json
from typing import Dict, Set, Optional
from datetime import datetime
import logging
from .event_manager import EventManager
from .message_formatter import MessageFormatter
from .sync_engine import SyncEngine
from .offline_queue import OfflineQueue
from .models import Event, EventType, ConnectionMetrics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
event_manager: Optional[EventManager] = None
message_formatter: Optional[MessageFormatter] = None
sync_engine: Optional[SyncEngine] = None
offline_queue: Optional[OfflineQueue] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global event_manager, message_formatter, sync_engine, offline_queue
    
    # Initialize components
    event_manager = EventManager()
    message_formatter = MessageFormatter()
    sync_engine = SyncEngine()
    offline_queue = OfflineQueue()
    
    # Start background tasks
    asyncio.create_task(event_manager.process_events())
    asyncio.create_task(offline_queue.process_queue())
    
    logger.info("Real-time API system started")
    yield
    
    # Cleanup
    logger.info("Shutting down Real-time API system")

app = FastAPI(title="Real-time API Design", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"service": "Real-time API Design", "status": "running"}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "active_connections": len(event_manager.connections),
        "queued_events": await offline_queue.get_queue_size()
    }

@app.get("/metrics")
async def get_metrics():
    metrics = event_manager.get_metrics()
    return {
        "connections": {
            "active": metrics["active_connections"],
            "total_connected": metrics["total_connected"],
            "total_disconnected": metrics["total_disconnected"]
        },
        "events": {
            "total_sent": metrics["total_events_sent"],
            "total_received": metrics["total_events_received"],
            "events_by_type": metrics["events_by_type"]
        },
        "sync": {
            "conflicts_detected": sync_engine.get_conflict_count(),
            "conflicts_resolved": sync_engine.get_resolved_count()
        },
        "offline": {
            "queued_events": await offline_queue.get_queue_size()
        }
    }

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    logger.info(f"Client {client_id} connected")
    
    # Register connection
    await event_manager.register_connection(client_id, websocket)
    
    # Send pending offline events
    pending_events = await offline_queue.get_pending_events(client_id)
    for event in pending_events:
        try:
            formatted_msg = message_formatter.format_message(event)
            await websocket.send_json(formatted_msg)
            event_manager.increment_events_sent()
        except Exception as e:
            logger.error(f"Error sending pending event: {e}")
    
    try:
        while True:
            data = await websocket.receive_json()
            
            # Parse incoming message
            event_type = data.get("type")
            payload = data.get("payload", {})
            version = data.get("version", 0)
            
            # Create event
            event = Event(
                type=EventType(event_type),
                payload=payload,
                client_id=client_id,
                version=version
            )
            
            # Check for conflicts
            conflict = sync_engine.detect_conflict(event)
            conflict_detected = conflict is not None
            if conflict:
                resolved_event = sync_engine.resolve_conflict(event, conflict)
                event = resolved_event
            
            # Update client state
            sync_engine.update_state(client_id, event)
            
            # Broadcast to all clients
            await event_manager.broadcast_event(event, exclude_client=client_id)
            
            # Send acknowledgment with conflict information
            ack_msg = message_formatter.format_acknowledgment(event, conflict_detected=conflict_detected)
            await websocket.send_json(ack_msg)
            # Count acknowledgment as an event sent
            event_manager.increment_events_sent()
            logger.info(f"Event processed: type={event.type.value}, conflict={conflict_detected}, events_sent={event_manager.metrics['total_events_sent']}")
            
    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected")
        await event_manager.unregister_connection(client_id)
        
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
        await event_manager.unregister_connection(client_id)

@app.post("/api/events")
async def create_event(event_data: dict):
    """Create a server-side event to broadcast to all clients"""
    try:
        event = Event(
            type=EventType(event_data.get("type")),
            payload=event_data.get("payload", {}),
            client_id="server"
        )
        
        await event_manager.broadcast_event(event)
        return {"status": "success", "event_id": event.id}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/state/{client_id}")
async def get_client_state(client_id: str):
    """Get current synchronized state for a client"""
    state = sync_engine.get_client_state(client_id)
    return {"client_id": client_id, "state": state}
