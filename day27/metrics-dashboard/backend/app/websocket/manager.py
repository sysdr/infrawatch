from fastapi import WebSocket
from typing import List, Dict
import json
import asyncio
import random
from datetime import datetime

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.metric_subscriptions: Dict[WebSocket, List[str]] = {}
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.metric_subscriptions[websocket] = []
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.metric_subscriptions:
            del self.metric_subscriptions[websocket]
    
    async def send_message(self, websocket: WebSocket, message: dict):
        try:
            await websocket.send_text(json.dumps(message))
        except:
            self.disconnect(websocket)
    
    async def broadcast_metric(self, metric_name: str, value: float, labels: dict = {}):
        """Broadcast metric update to subscribed clients"""
        message = {
            "type": "metric_update",
            "metric_name": metric_name,
            "value": value,
            "timestamp": datetime.utcnow().isoformat(),
            "labels": labels
        }
        
        for websocket in self.active_connections.copy():
            if metric_name in self.metric_subscriptions.get(websocket, []):
                await self.send_message(websocket, message)
    
    async def subscribe_metric(self, websocket: WebSocket, metric_name: str):
        """Subscribe websocket to metric updates"""
        if websocket not in self.metric_subscriptions:
            self.metric_subscriptions[websocket] = []
        
        if metric_name not in self.metric_subscriptions[websocket]:
            self.metric_subscriptions[websocket].append(metric_name)
    
    async def unsubscribe_metric(self, websocket: WebSocket, metric_name: str):
        """Unsubscribe websocket from metric updates"""
        if websocket in self.metric_subscriptions:
            if metric_name in self.metric_subscriptions[websocket]:
                self.metric_subscriptions[websocket].remove(metric_name)

manager = WebSocketManager()

# Simulate real-time metrics
async def generate_sample_metrics():
    """Generate sample metrics for demo"""
    metrics = {
        "cpu_usage": lambda: random.uniform(20, 80),
        "memory_usage": lambda: random.uniform(30, 90),
        "network_io": lambda: random.uniform(100, 1000),
        "disk_io": lambda: random.uniform(50, 500),
        "request_rate": lambda: random.uniform(10, 200)
    }
    
    while True:
        for metric_name, value_func in metrics.items():
            value = value_func()
            await manager.broadcast_metric(metric_name, value)
        await asyncio.sleep(1)  # Update every second
