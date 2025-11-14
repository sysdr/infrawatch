import asyncio
from fastapi import WebSocket
from typing import Dict, Set
from datetime import datetime
import logging
from .models import Event

logger = logging.getLogger(__name__)

class EventManager:
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.metrics = {
            "active_connections": 0,
            "total_connected": 0,
            "total_disconnected": 0,
            "total_events_sent": 0,
            "total_events_received": 0,
            "events_by_type": {}
        }
    
    async def register_connection(self, client_id: str, websocket: WebSocket):
        self.connections[client_id] = websocket
        self.metrics["active_connections"] = len(self.connections)
        self.metrics["total_connected"] += 1
        logger.info(f"Registered connection: {client_id}")
    
    async def unregister_connection(self, client_id: str):
        if client_id in self.connections:
            del self.connections[client_id]
            self.metrics["active_connections"] = len(self.connections)
            self.metrics["total_disconnected"] += 1
            logger.info(f"Unregistered connection: {client_id}")
    
    def increment_events_sent(self, count: int = 1):
        """Increment the total events sent counter"""
        self.metrics["total_events_sent"] += count
        logger.debug(f"Incremented events_sent by {count}, total now: {self.metrics['total_events_sent']}")
    
    async def broadcast_event(self, event: Event, exclude_client: str = None):
        """Broadcast event to all connected clients except excluded one"""
        await self.event_queue.put((event, exclude_client))
        self.metrics["total_events_received"] += 1
        
        # Track event type
        event_type = event.type.value
        self.metrics["events_by_type"][event_type] = \
            self.metrics["events_by_type"].get(event_type, 0) + 1
    
    async def process_events(self):
        """Background task to process and send events"""
        while True:
            try:
                event, exclude_client = await self.event_queue.get()
                
                disconnected = []
                for client_id, websocket in self.connections.items():
                    if client_id == exclude_client:
                        continue
                    
                    try:
                        message = {
                            "type": event.type.value,
                            "payload": event.payload,
                            "id": event.id,
                            "timestamp": event.timestamp.isoformat(),
                            "version": event.version,
                            "client_id": event.client_id
                        }
                        await websocket.send_json(message)
                        self.metrics["total_events_sent"] += 1
                        
                    except Exception as e:
                        logger.error(f"Failed to send to {client_id}: {e}")
                        disconnected.append(client_id)
                
                # Clean up disconnected clients
                for client_id in disconnected:
                    await self.unregister_connection(client_id)
                    
            except Exception as e:
                logger.error(f"Error processing events: {e}")
                await asyncio.sleep(0.1)
    
    def get_metrics(self):
        return self.metrics.copy()
