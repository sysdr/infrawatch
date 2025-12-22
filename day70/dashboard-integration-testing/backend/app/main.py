from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Set
import random

from app.core.config import settings
from app.services.metric_generator import MetricGenerator
from app.services.connection_manager import ConnectionManager
from app.core.redis_client import get_redis_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.redis = await get_redis_client()
    app.state.connection_manager = ConnectionManager()
    app.state.metric_generator = MetricGenerator()
    
    # Start metric generation background task
    app.state.metric_task = asyncio.create_task(
        generate_metrics(app.state.connection_manager, app.state.metric_generator)
    )
    
    yield
    
    # Shutdown
    app.state.metric_task.cancel()
    await app.state.redis.close()

app = FastAPI(title="Dashboard Integration Testing API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MetricBatcher:
    """Batches metrics for efficient broadcasting"""
    def __init__(self, batch_window_ms: int = 1000):
        self.batch_window = batch_window_ms / 1000
        self.buffer: List[Dict] = []
        self.priority_buffer: List[Dict] = []
        self.last_flush = time.time()
        
    def add(self, metric: Dict):
        if metric.get('priority') == 'critical':
            self.priority_buffer.append(metric)
        else:
            self.buffer.append(metric)
            
    def should_flush(self) -> bool:
        return (time.time() - self.last_flush) >= self.batch_window
        
    def flush(self) -> tuple[List[Dict], List[Dict]]:
        regular = self.buffer.copy()
        priority = self.priority_buffer.copy()
        self.buffer.clear()
        self.priority_buffer.clear()
        self.last_flush = time.time()
        return regular, priority

batcher = MetricBatcher()

async def generate_metrics(manager: ConnectionManager, generator: MetricGenerator):
    """Background task to generate and broadcast metrics"""
    while True:
        try:
            # Generate metrics based on current load simulation
            metrics = await generator.generate_batch(size=2)
            
            for metric in metrics:
                batcher.add(metric)
            
            # Check if we should flush batch
            if batcher.should_flush():
                regular, priority = batcher.flush()
                
                # Send priority metrics immediately
                if priority:
                    await manager.broadcast({
                        'type': 'metrics_priority',
                        'data': priority,
                        'timestamp': datetime.utcnow().isoformat()
                    })
                
                # Send regular metrics in batch
                if regular:
                    await manager.broadcast({
                        'type': 'metrics_batch',
                        'data': regular,
                        'timestamp': datetime.utcnow().isoformat()
                    })
            
            await asyncio.sleep(0.5)  # 2 metrics/second base rate (slowed down for visibility)
            
        except Exception as e:
            print(f"Error generating metrics: {e}")
            await asyncio.sleep(1)

@app.websocket("/ws/dashboard/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time dashboard updates"""
    await app.state.connection_manager.connect(websocket, client_id)
    
    try:
        # Send initial connection confirmation
        await websocket.send_json({
            'type': 'connected',
            'client_id': client_id,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        while True:
            data = await websocket.receive_json()
            
            # Handle different message types
            if data.get('type') == 'ping':
                await websocket.send_json({
                    'type': 'pong',
                    'timestamp': datetime.utcnow().isoformat()
                })
            elif data.get('type') == 'subscribe':
                # Client subscribing to specific metric streams
                await websocket.send_json({
                    'type': 'subscribed',
                    'channels': data.get('channels', []),
                    'timestamp': datetime.utcnow().isoformat()
                })
            elif data.get('type') == 'set_load':
                # Adjust load simulation
                load_level = data.get('load', 'normal')
                app.state.metric_generator.set_load_level(load_level)
                await websocket.send_json({
                    'type': 'load_updated',
                    'load': load_level,
                    'timestamp': datetime.utcnow().isoformat()
                })
                
    except WebSocketDisconnect:
        app.state.connection_manager.disconnect(client_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        app.state.connection_manager.disconnect(client_id)

@app.get("/api/metrics/history")
async def get_metric_history(limit: int = 1000):
    """Get historical metrics for initial dashboard load"""
    metrics = await app.state.metric_generator.get_history(limit)
    return {
        'metrics': metrics,
        'count': len(metrics),
        'timestamp': datetime.utcnow().isoformat()
    }

@app.get("/api/performance/stats")
async def get_performance_stats():
    """Get current performance statistics"""
    return {
        'connected_clients': len(app.state.connection_manager.active_connections),
        'metrics_per_second': app.state.metric_generator.get_rate(),
        'memory_usage_mb': app.state.metric_generator.get_memory_usage(),
        'uptime_seconds': app.state.metric_generator.get_uptime(),
        'timestamp': datetime.utcnow().isoformat()
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
