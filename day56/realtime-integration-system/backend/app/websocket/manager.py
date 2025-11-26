from fastapi import WebSocket
from typing import Dict, List, Any
import asyncio
import structlog
from datetime import datetime
from app.core.metrics import MetricsCollector

logger = structlog.get_logger()

class WebSocketManager:
    """Manages WebSocket connections with reconnection support"""
    
    def __init__(self, metrics: MetricsCollector):
        self.connections: Dict[str, WebSocket] = {}
        self.connection_metadata: Dict[str, Dict] = {}
        self.metrics = metrics
        self.heartbeat_task = None
    
    async def connect(self, client_id: str, websocket: WebSocket):
        """Accept new connection"""
        await websocket.accept()
        self.connections[client_id] = websocket
        self.connection_metadata[client_id] = {
            "connected_at": datetime.now(),
            "last_heartbeat": datetime.now(),
            "reconnect_count": self.connection_metadata.get(client_id, {}).get("reconnect_count", 0)
        }
        
        self.metrics.increment_counter("ws_connections")
        logger.info("Client connected", 
                   client_id=client_id, 
                   total_connections=len(self.connections))
        
        # Send connection acknowledgment
        await websocket.send_json({
            "type": "connected",
            "client_id": client_id,
            "timestamp": datetime.now().isoformat()
        })
    
    async def disconnect(self, client_id: str):
        """Remove connection"""
        if client_id in self.connections:
            try:
                await self.connections[client_id].close()
            except:
                pass
            del self.connections[client_id]
            self.metrics.increment_counter("ws_disconnections")
            logger.info("Client disconnected", 
                       client_id=client_id,
                       total_connections=len(self.connections))
    
    async def send_to_client(self, client_id: str, message: Dict[str, Any]):
        """Send message to specific client"""
        if client_id in self.connections:
            try:
                start_time = datetime.now()
                await self.connections[client_id].send_json(message)
                
                latency = (datetime.now() - start_time).total_seconds() * 1000
                self.metrics.record_latency("ws_send", latency)
                
            except Exception as e:
                logger.error("Failed to send message", 
                           client_id=client_id, 
                           error=str(e))
                await self.disconnect(client_id)
    
    async def broadcast(self, message: Dict[str, Any], exclude: List[str] = None):
        """Broadcast message to all clients"""
        exclude = exclude or []
        tasks = []
        
        for client_id in list(self.connections.keys()):
            if client_id not in exclude:
                tasks.append(self.send_to_client(client_id, message))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def disconnect_all(self):
        """Disconnect all clients gracefully"""
        for client_id in list(self.connections.keys()):
            await self.disconnect(client_id)
    
    def get_connection_count(self) -> int:
        """Get active connection count"""
        return len(self.connections)
    
    async def heartbeat(self):
        """Send periodic heartbeat to all connections"""
        while True:
            await asyncio.sleep(30)
            
            for client_id in list(self.connections.keys()):
                try:
                    await self.send_to_client(client_id, {
                        "type": "heartbeat",
                        "timestamp": datetime.now().isoformat()
                    })
                    self.connection_metadata[client_id]["last_heartbeat"] = datetime.now()
                except Exception as e:
                    logger.error("Heartbeat failed", client_id=client_id)
