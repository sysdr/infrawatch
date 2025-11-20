import asyncio
import json
import math
import time
from dataclasses import dataclass, field
from typing import List, Optional

import statistics
import websockets

@dataclass
class ConnectionMetrics:
    connection_time_ms: float = 0
    messages_sent: int = 0
    messages_received: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    latencies: List[float] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    @property
    def avg_latency(self) -> float:
        return statistics.mean(self.latencies) if self.latencies else 0
    
    @property
    def p95_latency(self) -> float:
        if not self.latencies:
            return 0
        sorted_lat = sorted(self.latencies)
        idx = math.ceil(len(sorted_lat) * 0.95) - 1
        return sorted_lat[max(0, min(idx, len(sorted_lat) - 1))]
    
    @property
    def p99_latency(self) -> float:
        if not self.latencies:
            return 0
        sorted_lat = sorted(self.latencies)
        idx = math.ceil(len(sorted_lat) * 0.99) - 1
        return sorted_lat[max(0, min(idx, len(sorted_lat) - 1))]

class WebSocketTestClient:
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.metrics = ConnectionMetrics()
        self.connected = False
        self._receive_task = None
        self._received_messages: List[dict] = []
        
    async def connect(self, url: str, headers: dict = None, timeout: float = 30.0):
        start_time = time.time()
        try:
            connect_kwargs = {"open_timeout": timeout}
            if headers:
                connect_kwargs["extra_headers"] = headers
            self.ws = await websockets.connect(
                f"{url}/{self.client_id}",
                **connect_kwargs
            )
            self.metrics.connection_time_ms = (time.time() - start_time) * 1000
            self.connected = True
            self._receive_task = asyncio.create_task(self._receive_loop())
        except Exception as e:
            self.metrics.errors.append(str(e))
            raise
            
    async def _receive_loop(self):
        try:
            async for message in self.ws:
                self.metrics.messages_received += 1
                self.metrics.bytes_received += len(message)
                data = json.loads(message)
                self._received_messages.append(data)
                
                # Record latency for pong messages
                if data.get("type") == "pong" and "client_time" in data:
                    latency = time.time() * 1000 - data["client_time"]
                    self.metrics.latencies.append(latency)
        except websockets.exceptions.ConnectionClosed:
            self.connected = False
        except Exception as e:
            self.metrics.errors.append(str(e))
            self.connected = False
            
    async def send(self, message: dict):
        if not self.ws or not self.connected:
            raise RuntimeError("Not connected")
        data = json.dumps(message)
        await self.ws.send(data)
        self.metrics.messages_sent += 1
        self.metrics.bytes_sent += len(data)
        
    async def ping(self):
        await self.send({
            "type": "ping",
            "timestamp": time.time() * 1000
        })
        
    async def send_message(self, content: str):
        await self.send({
            "type": "message",
            "content": content
        })
        
    async def receive(self, timeout: float = 5.0) -> dict:
        start = time.time()
        while time.time() - start < timeout:
            if self._received_messages:
                return self._received_messages.pop(0)
            await asyncio.sleep(0.01)
        raise TimeoutError("No message received within timeout")
        
    async def close(self):
        if self._receive_task:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass
        if self.ws:
            await self.ws.close()
        self.connected = False
        
    def get_metrics(self) -> ConnectionMetrics:
        return self.metrics
