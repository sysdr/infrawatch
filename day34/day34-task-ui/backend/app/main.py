from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import json
import asyncio
import redis
from datetime import datetime
from typing import List
import uvicorn

app = FastAPI(title="Task Management Dashboard", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Sample task data
tasks_db = [
    {
        "id": f"task-{i}",
        "name": f"Process Data Batch {i}",
        "status": "completed" if i % 3 == 0 else ("running" if i % 2 == 0 else "pending"),
        "queue": "default",
        "created_at": datetime.now().isoformat(),
        "completed_at": datetime.now().isoformat() if i % 3 == 0 else None,
        "duration": 120 + (i * 10) if i % 3 == 0 else None,
        "retry_count": i % 4,
        "worker": f"worker-{i % 5}",
        "progress": 100 if i % 3 == 0 else (50 if i % 2 == 0 else 0)
    }
    for i in range(1, 51)
]

queue_stats = {
    "default": {"pending": 15, "running": 8, "completed": 120, "failed": 3},
    "priority": {"pending": 5, "running": 3, "completed": 45, "failed": 1},
    "batch": {"pending": 22, "running": 4, "completed": 89, "failed": 7}
}

@app.get("/api/tasks")
async def get_tasks(limit: int = 20, offset: int = 0, status: str = None, queue: str = None):
    filtered_tasks = tasks_db
    
    if status:
        filtered_tasks = [t for t in filtered_tasks if t["status"] == status]
    if queue:
        filtered_tasks = [t for t in filtered_tasks if t["queue"] == queue]
    
    total = len(filtered_tasks)
    paginated = filtered_tasks[offset:offset+limit]
    
    return {
        "tasks": paginated,
        "total": total,
        "limit": limit,
        "offset": offset
    }

@app.get("/api/queues")
async def get_queues():
    return {"queues": queue_stats}

@app.get("/api/metrics")
async def get_metrics():
    return {
        "throughput": {"current": 145, "average": 132, "peak": 189},
        "latency": {"p50": 85, "p90": 156, "p99": 234},
        "errors": {"rate": 2.3, "count": 12, "last_hour": 8},
        "workers": {"active": 15, "idle": 3, "total": 18}
    }

@app.post("/api/tasks/{task_id}/retry")
async def retry_task(task_id: str):
    task = next((t for t in tasks_db if t["id"] == task_id), None)
    if task:
        task["status"] = "pending"
        task["retry_count"] += 1
        await manager.broadcast(json.dumps({
            "type": "task_updated",
            "task": task
        }))
        return {"message": "Task queued for retry"}
    return {"error": "Task not found"}

@app.post("/api/tasks/{task_id}/cancel")
async def cancel_task(task_id: str):
    task = next((t for t in tasks_db if t["id"] == task_id), None)
    if task:
        task["status"] = "cancelled"
        await manager.broadcast(json.dumps({
            "type": "task_updated", 
            "task": task
        }))
        return {"message": "Task cancelled"}
    return {"error": "Task not found"}

@app.post("/api/queues/{queue_name}/start")
async def start_queue(queue_name: str):
    await manager.broadcast(json.dumps({
        "type": "queue_started",
        "queue": queue_name
    }))
    return {"message": f"Queue {queue_name} started"}

@app.post("/api/queues/{queue_name}/pause")
async def pause_queue(queue_name: str):
    await manager.broadcast(json.dumps({
        "type": "queue_paused",
        "queue": queue_name
    }))
    return {"message": f"Queue {queue_name} paused"}

@app.post("/api/queues/{queue_name}/restart")
async def restart_queue(queue_name: str):
    await manager.broadcast(json.dumps({
        "type": "queue_restarted",
        "queue": queue_name
    }))
    return {"message": f"Queue {queue_name} restarted"}

@app.post("/api/queues/{queue_name}/clear")
async def clear_queue(queue_name: str):
    # Clear tasks from the queue (in a real implementation, this would clear from Redis)
    await manager.broadcast(json.dumps({
        "type": "queue_cleared",
        "queue": queue_name
    }))
    return {"message": f"Queue {queue_name} cleared"}

@app.post("/api/queues/{queue_name}/configure")
async def configure_queue(queue_name: str):
    await manager.broadcast(json.dumps({
        "type": "queue_configured",
        "queue": queue_name
    }))
    return {"message": f"Queue {queue_name} configuration updated"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Send periodic updates
            await asyncio.sleep(2)
            metrics_update = {
                "type": "metrics_update",
                "metrics": {
                    "throughput": {"current": 145 + (asyncio.get_event_loop().time() % 50)},
                    "active_tasks": len([t for t in tasks_db if t["status"] == "running"]),
                    "timestamp": datetime.now().isoformat()
                }
            }
            await manager.send_personal_message(json.dumps(metrics_update), websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
