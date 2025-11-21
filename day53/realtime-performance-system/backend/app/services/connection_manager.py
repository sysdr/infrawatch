import os
import asyncio
import logging
import gzip
import json
from datetime import datetime
from collections import deque, defaultdict
from fastapi import WebSocket
from typing import Dict, Set
from ..utils.redis_queue import redis_queue
from ..models.notification import NotificationBatch

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_subscriptions: Dict[str, Set[str]] = defaultdict(set)
        self.message_buffers: Dict[str, deque] = {}
        self.batch_size = int(os.getenv("MESSAGE_BATCH_SIZE", 50))
        self.batch_interval = float(os.getenv("MESSAGE_BATCH_INTERVAL", 0.1))
        self.metrics = {
            'total_messages': 0,
            'total_bytes_sent': 0,
            'compression_savings': 0
        }
        
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept WebSocket connection and initialize user buffer"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.message_buffers[user_id] = deque(maxlen=100)  # Circular buffer
        logger.info(f"User {user_id} connected. Total connections: {len(self.active_connections)}")
    
    async def disconnect(self, user_id: str):
        """Remove connection and cleanup resources"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.message_buffers:
            del self.message_buffers[user_id]
        if user_id in self.user_subscriptions:
            del self.user_subscriptions[user_id]
        logger.info(f"User {user_id} disconnected. Total connections: {len(self.active_connections)}")
    
    async def add_to_buffer(self, user_id: str, notification: dict):
        """Add notification to user's message buffer"""
        if user_id in self.message_buffers:
            self.message_buffers[user_id].append(notification)
            
            # Send batch if buffer is full
            if len(self.message_buffers[user_id]) >= self.batch_size:
                await self.flush_buffer(user_id)
    
    async def flush_buffer(self, user_id: str):
        """Send batched messages to user"""
        if user_id not in self.message_buffers or not self.message_buffers[user_id]:
            return
        
        if user_id not in self.active_connections:
            return
        
        try:
            # Create batch
            notifications = list(self.message_buffers[user_id])
            batch = NotificationBatch(
                notifications=notifications,
                count=len(notifications),
                timestamp=datetime.now()
            )
            
            # Serialize and compress
            json_data = batch.model_dump_json()
            original_size = len(json_data.encode())
            compressed = gzip.compress(json_data.encode())
            compressed_size = len(compressed)
            
            # Track metrics
            self.metrics['total_messages'] += len(notifications)
            self.metrics['total_bytes_sent'] += compressed_size
            self.metrics['compression_savings'] += (original_size - compressed_size)
            
            # Send compressed batch
            websocket = self.active_connections[user_id]
            await websocket.send_bytes(compressed)
            
            # Clear buffer
            self.message_buffers[user_id].clear()
            
            logger.debug(f"Flushed {len(notifications)} messages to {user_id} "
                        f"(compressed: {compressed_size}B, saved: {original_size - compressed_size}B)")
        
        except Exception as e:
            logger.error(f"Error flushing buffer for {user_id}: {e}")
            await self.disconnect(user_id)
    
    async def start_batch_flusher(self):
        """Periodically flush message buffers"""
        while True:
            await asyncio.sleep(self.batch_interval)
            for user_id in list(self.message_buffers.keys()):
                if self.message_buffers[user_id]:
                    await self.flush_buffer(user_id)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected users"""
        for user_id in list(self.active_connections.keys()):
            await self.add_to_buffer(user_id, message)
    
    def get_connection_count(self) -> int:
        """Get active connection count"""
        return len(self.active_connections)
    
    def get_metrics(self) -> dict:
        """Get connection manager metrics"""
        return {
            **self.metrics,
            'active_connections': len(self.active_connections),
            'compression_ratio': (
                self.metrics['compression_savings'] / self.metrics['total_bytes_sent'] 
                if self.metrics['total_bytes_sent'] > 0 else 0
            )
        }

manager = ConnectionManager()
