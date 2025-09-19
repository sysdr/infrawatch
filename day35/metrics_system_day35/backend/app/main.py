from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import asyncio
from datetime import datetime, timedelta
import uuid

from .database import engine, get_db
from .models import Task, TaskStatus, TaskResult, Base
from .services.task_service import TaskService, TaskPriority
from .services.metrics_service import MetricsService
from .workers.celery_app import celery_app
from .api.schemas import TaskCreate, TaskResponse, TaskStats

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Metrics Collection System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

task_service = TaskService()
metrics_service = MetricsService()

# WebSocket connections for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Send periodic updates
            stats = await task_service.get_task_stats()
            await websocket.send_text(json.dumps({
                "type": "stats_update",
                "data": stats
            }))
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/api/tasks", response_model=TaskResponse)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Create a new background task"""
    try:
        db_task = await task_service.create_task(
            task_type=task.task_type,
            payload=task.payload,
            priority=task.priority,
            db=db
        )
        
        # Queue task in Celery
        celery_task = celery_app.send_task(
            'process_metrics_task',
            args=[db_task.id],
            queue='default',
            priority=task.priority.value
        )
        
        # Update task with celery ID
        db_task.celery_id = celery_task.id
        db.commit()
        
        return TaskResponse.from_orm(db_task)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/tasks", response_model=List[TaskResponse])
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    status: Optional[TaskStatus] = None,
    db: Session = Depends(get_db)
):
    """Get tasks with pagination and filtering"""
    tasks = await task_service.get_tasks(skip=skip, limit=limit, status=status, db=db)
    return [TaskResponse.from_orm(task) for task in tasks]

@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, db: Session = Depends(get_db)):
    """Get specific task by ID"""
    task = await task_service.get_task(task_id, db)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.from_orm(task)

@app.post("/api/tasks/{task_id}/retry")
async def retry_task(task_id: str, db: Session = Depends(get_db)):
    """Retry a failed task"""
    success = await task_service.retry_task(task_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found or cannot retry")
    return {"message": "Task retry initiated"}

@app.delete("/api/tasks/{task_id}")
async def cancel_task(task_id: str, db: Session = Depends(get_db)):
    """Cancel a running task"""
    success = await task_service.cancel_task(task_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found or cannot cancel")
    return {"message": "Task cancelled"}

@app.get("/api/stats", response_model=TaskStats)
async def get_stats(db: Session = Depends(get_db)):
    """Get system statistics"""
    return await task_service.get_task_stats(db)

@app.get("/api/metrics")
async def get_metrics():
    """Get Prometheus metrics"""
    return metrics_service.get_metrics()

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
