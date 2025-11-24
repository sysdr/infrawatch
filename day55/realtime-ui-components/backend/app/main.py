from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import json
import time
import random
from datetime import datetime
from typing import Dict, Set
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store active connections
active_connections: Set[WebSocket] = set()
connection_quality: Dict[str, dict] = {}

# Metrics storage
metrics = {
    "user_count": 100,  # Initialize with non-zero value
    "message_rate": 0,
    "messages_history": [],
    "latency_history": []
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start background tasks
    task1 = asyncio.create_task(simulate_user_activity())
    task2 = asyncio.create_task(simulate_message_traffic())
    task3 = asyncio.create_task(broadcast_metrics())
    yield
    # Cleanup
    task1.cancel()
    task2.cancel()
    task3.cancel()

app = FastAPI(title="Real-time UI Components", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def simulate_user_activity():
    """Simulate user count changes"""
    while True:
        await asyncio.sleep(2)
        # Simulate user count fluctuation
        change = random.randint(-5, 10)
        metrics["user_count"] = max(50, min(500, metrics["user_count"] + change))
        
        await broadcast_message({
            "type": "user_count",
            "data": {
                "count": metrics["user_count"],
                "timestamp": datetime.now().isoformat()
            }
        })

async def simulate_message_traffic():
    """Simulate message traffic for rate calculations"""
    while True:
        await asyncio.sleep(0.5)
        # Generate random message burst
        messages = random.randint(10, 50)
        timestamp = time.time()
        
        metrics["messages_history"].append({
            "count": messages,
            "timestamp": timestamp
        })
        
        # Keep only last 60 seconds
        cutoff = timestamp - 60
        metrics["messages_history"] = [
            m for m in metrics["messages_history"] 
            if m["timestamp"] > cutoff
        ]
        
        # Calculate rate
        total_messages = sum(m["count"] for m in metrics["messages_history"])
        metrics["message_rate"] = total_messages / 60
        
        await broadcast_message({
            "type": "message_rate",
            "data": {
                "rate": round(metrics["message_rate"], 2),
                "timestamp": datetime.now().isoformat()
            }
        })

async def broadcast_metrics():
    """Broadcast aggregated metrics periodically"""
    while True:
        await asyncio.sleep(1)
        
        # Simulate latency
        latency = random.randint(20, 100) + (random.random() * 50 if random.random() > 0.8 else 0)
        metrics["latency_history"].append(latency)
        if len(metrics["latency_history"]) > 20:
            metrics["latency_history"].pop(0)
        
        await broadcast_message({
            "type": "metrics",
            "data": {
                "user_count": metrics["user_count"],
                "message_rate": round(metrics["message_rate"], 2),
                "latency": round(latency, 2),
                "timestamp": datetime.now().isoformat()
            }
        })

async def broadcast_message(message: dict):
    """Broadcast message to all connected clients"""
    disconnected = set()
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except Exception as e:
            logger.error(f"Error broadcasting to client: {e}")
            disconnected.add(connection)
    
    # Remove disconnected clients
    for conn in disconnected:
        active_connections.discard(conn)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    client_id = id(websocket)
    
    logger.info(f"Client {client_id} connected. Total: {len(active_connections)}")
    
    # Send initial state
    await websocket.send_json({
        "type": "connection",
        "data": {
            "status": "connected",
            "client_id": client_id,
            "timestamp": datetime.now().isoformat()
        }
    })
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "ping":
                # Respond to ping with pong
                await websocket.send_json({
                    "type": "pong",
                    "data": {
                        "timestamp": datetime.now().isoformat(),
                        "latency": data.get("data", {}).get("client_timestamp")
                    }
                })
            elif data.get("type") == "message":
                # Echo message back with confirmation
                await websocket.send_json({
                    "type": "message_ack",
                    "data": {
                        "id": data.get("data", {}).get("id"),
                        "status": "delivered",
                        "timestamp": datetime.now().isoformat()
                    }
                })
                
    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected")
    except Exception as e:
        logger.error(f"Error in websocket: {e}")
    finally:
        active_connections.discard(websocket)
        logger.info(f"Client {client_id} removed. Total: {len(active_connections)}")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "connections": len(active_connections),
        "metrics": {
            "user_count": metrics["user_count"],
            "message_rate": round(metrics["message_rate"], 2)
        }
    }

@app.get("/api/stats")
async def get_stats():
    """REST endpoint for stats (fallback when WebSocket unavailable)"""
    return {
        "user_count": metrics["user_count"],
        "message_rate": round(metrics["message_rate"], 2),
        "latency": round(sum(metrics["latency_history"]) / len(metrics["latency_history"]), 2) if metrics["latency_history"] else 0,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
