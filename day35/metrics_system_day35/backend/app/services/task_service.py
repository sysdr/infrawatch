from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from ..models import Task, TaskStatus, TaskPriority, TaskResult
from ..api.schemas import TaskStats

class TaskService:
    async def create_task(
        self,
        task_type: str,
        payload: Dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
        db: Session = None
    ) -> Task:
        """Create a new task"""
        task = Task(
            task_type=task_type,
            payload=payload,
            priority=priority,
            status=TaskStatus.PENDING
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task
    
    async def get_tasks(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[TaskStatus] = None,
        db: Session = None
    ) -> List[Task]:
        """Get tasks with filtering"""
        query = db.query(Task)
        
        if status:
            query = query.filter(Task.status == status)
        
        return query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
    
    async def get_task(self, task_id: str, db: Session) -> Optional[Task]:
        """Get task by ID"""
        return db.query(Task).filter(Task.id == task_id).first()
    
    async def retry_task(self, task_id: str, db: Session) -> bool:
        """Retry a failed task"""
        task = db.query(Task).filter(Task.id == task_id).first()
        
        if not task or task.status not in [TaskStatus.FAILED, TaskStatus.CANCELLED]:
            return False
        
        task.status = TaskStatus.PENDING
        task.retry_count += 1
        task.error_message = None
        task.started_at = None
        task.completed_at = None
        
        db.commit()
        return True
    
    async def cancel_task(self, task_id: str, db: Session) -> bool:
        """Cancel a running task"""
        task = db.query(Task).filter(Task.id == task_id).first()
        
        if not task or task.status not in [TaskStatus.PENDING, TaskStatus.PROCESSING]:
            return False
        
        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.utcnow()
        
        db.commit()
        return True
    
    async def get_task_stats(self, db: Session = None) -> TaskStats:
        """Get comprehensive task statistics"""
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        day_ago = now - timedelta(days=1)
        
        # Total counts by status
        total_tasks = db.query(func.count(Task.id)).scalar()
        
        status_counts = db.query(
            Task.status,
            func.count(Task.id)
        ).group_by(Task.status).all()
        
        # Recent activity (last hour)
        recent_tasks = db.query(func.count(Task.id)).filter(
            Task.created_at >= hour_ago
        ).scalar()
        
        # Success rate (last 24 hours)
        recent_completed = db.query(func.count(Task.id)).filter(
            and_(
                Task.completed_at >= day_ago,
                Task.status.in_([TaskStatus.SUCCESS, TaskStatus.FAILED])
            )
        ).scalar()
        
        recent_successful = db.query(func.count(Task.id)).filter(
            and_(
                Task.completed_at >= day_ago,
                Task.status == TaskStatus.SUCCESS
            )
        ).scalar()
        
        success_rate = (recent_successful / recent_completed * 100) if recent_completed > 0 else 0
        
        # Average execution time
        avg_execution = db.query(func.avg(Task.execution_time)).filter(
            and_(
                Task.execution_time.isnot(None),
                Task.completed_at >= day_ago
            )
        ).scalar() or 0
        
        # Queue sizes by priority
        queue_stats = db.query(
            Task.priority,
            func.count(Task.id)
        ).filter(Task.status == TaskStatus.PENDING).group_by(Task.priority).all()
        
        return TaskStats(
            total_tasks=total_tasks,
            pending_tasks=sum(count for status, count in status_counts if status == TaskStatus.PENDING),
            processing_tasks=sum(count for status, count in status_counts if status == TaskStatus.PROCESSING),
            completed_tasks=sum(count for status, count in status_counts if status == TaskStatus.SUCCESS),
            failed_tasks=sum(count for status, count in status_counts if status == TaskStatus.FAILED),
            success_rate=round(success_rate, 2),
            avg_execution_time=round(avg_execution, 2),
            tasks_per_hour=recent_tasks,
            queue_sizes={
                str(priority): count for priority, count in queue_stats
            }
        )
