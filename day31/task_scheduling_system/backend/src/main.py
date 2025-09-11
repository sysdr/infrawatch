from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
import os
from datetime import datetime, timedelta
import asyncio
import json

from .models.task import Task, TaskExecution, Worker, Base
from .utils.database import get_db, engine
from .services.scheduler import scheduler
from .services.priority_queue import PriorityQueue
from .services.load_balancer import LoadBalancer
from .workers.task_functions import task_functions

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Scheduling System",
    description="A comprehensive task scheduling and execution system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
priority_queue = PriorityQueue()
load_balancer = LoadBalancer()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.get("/api/tasks")
async def get_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks = db.query(Task).offset(skip).limit(limit).all()
    return tasks

@app.post("/api/tasks")
async def create_task(task_data: dict, db: Session = Depends(get_db)):
    task = Task(
        name=task_data["name"],
        task_function=task_data["task_function"],
        cron_expression=task_data["cron_expression"],
        priority=task_data.get("priority", 5),
        max_retries=task_data.get("max_retries", 3),
        timeout_seconds=task_data.get("timeout_seconds", 300),
        is_active=True
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Add to scheduler
    scheduler.add_task(task)
    
    return task

@app.get("/api/tasks/{task_id}")
async def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/api/tasks/{task_id}")
async def update_task(task_id: int, task_data: dict, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    for key, value in task_data.items():
        setattr(task, key, value)
    
    db.commit()
    db.refresh(task)
    
    # Update scheduler
    scheduler.update_task(task)
    
    return task

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Remove from scheduler
    scheduler.remove_task(task_id)
    
    db.delete(task)
    db.commit()
    
    return {"message": "Task deleted successfully"}

@app.get("/api/executions")
async def get_executions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    executions = db.query(TaskExecution).offset(skip).limit(limit).all()
    return executions

@app.get("/api/executions/{execution_id}")
async def get_execution(execution_id: int, db: Session = Depends(get_db)):
    execution = db.query(TaskExecution).filter(TaskExecution.id == execution_id).first()
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution

@app.get("/api/workers")
async def get_workers(db: Session = Depends(get_db)):
    workers = db.query(Worker).all()
    return workers

@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    total_tasks = db.query(Task).count()
    active_tasks = db.query(Task).filter(Task.is_active == True).count()
    total_executions = db.query(TaskExecution).count()
    successful_executions = db.query(TaskExecution).filter(TaskExecution.status == "completed").count()
    failed_executions = db.query(TaskExecution).filter(TaskExecution.status == "failed").count()
    running_executions = db.query(TaskExecution).filter(TaskExecution.status == "running").count()
    
    return {
        "total_tasks": total_tasks,
        "active_tasks": active_tasks,
        "total_executions": total_executions,
        "successful_executions": successful_executions,
        "failed_executions": failed_executions,
        "running_executions": running_executions,
        "success_rate": (successful_executions / total_executions * 100) if total_executions > 0 else 0
    }

@app.post("/api/tasks/{task_id}/execute")
async def execute_task_now(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Create execution
    execution = TaskExecution(
        task_id=task_id,
        status="running",
        started_at=datetime.utcnow()
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)
    
    # Execute task
    try:
        if task.task_function in task_functions:
            result = await task_functions[task.task_function]()
            execution.status = "completed"
            execution.result = json.dumps(result)
        else:
            execution.status = "failed"
            execution.error_message = f"Unknown task function: {task.task_function}"
    except Exception as e:
        execution.status = "failed"
        execution.error_message = str(e)
    finally:
        execution.completed_at = datetime.utcnow()
        db.commit()
    
    return execution

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
