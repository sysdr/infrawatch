import asyncio
import json
import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from ..models.task import TaskModel, TaskStatus
from ..models.worker import WorkerModel
from ..utils.database import get_db
from ..utils.logger import get_logger
from ..utils.metrics import MetricsCollector

logger = get_logger(__name__)

class MonitoringService:
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.alert_thresholds = {
            "queue_depth": 100,
            "error_rate": 0.1,
            "worker_memory": 0.8,
            "task_age_minutes": 30
        }
        self._monitoring_active = False
    
    async def initialize(self):
        """Initialize monitoring service"""
        logger.info("Initializing monitoring service")
        await self.metrics_collector.initialize()
    
    async def start_background_monitoring(self):
        """Start background monitoring tasks"""
        self._monitoring_active = True
        asyncio.create_task(self._monitor_workers())
        asyncio.create_task(self._monitor_queues())
        asyncio.create_task(self._collect_system_metrics())
        logger.info("Background monitoring started")
    
    async def _monitor_workers(self):
        """Monitor worker health and performance"""
        while self._monitoring_active:
            try:
                db = next(get_db())
                workers = db.query(WorkerModel).all()
                
                for worker in workers:
                    # Check heartbeat freshness
                    time_since_heartbeat = datetime.utcnow() - worker.last_heartbeat
                    if time_since_heartbeat > timedelta(minutes=5):
                        worker.status = "unhealthy"
                        worker.is_healthy = False
                        logger.warning(f"Worker {worker.id} marked unhealthy - no heartbeat")
                    
                    # Check resource usage
                    if worker.memory_usage > self.alert_thresholds["worker_memory"]:
                        logger.warning(f"Worker {worker.id} high memory usage: {worker.memory_usage:.2%}")
                        await self._trigger_alert("high_memory", {
                            "worker_id": worker.id,
                            "memory_usage": worker.memory_usage
                        })
                
                db.commit()
                db.close()
                
            except Exception as e:
                logger.error(f"Error monitoring workers: {e}")
            
            await asyncio.sleep(30)  # Check every 30 seconds
    
    async def _monitor_queues(self):
        """Monitor queue depth and task ages"""
        while self._monitoring_active:
            try:
                db = next(get_db())
                
                # Check queue depths
                queue_stats = db.query(
                    TaskModel.queue_name,
                    func.count(TaskModel.id).label('count')
                ).filter(
                    TaskModel.status.in_([TaskStatus.QUEUED, TaskStatus.PROCESSING])
                ).group_by(TaskModel.queue_name).all()
                
                for queue_name, depth in queue_stats:
                    if depth > self.alert_thresholds["queue_depth"]:
                        logger.warning(f"Queue {queue_name} depth: {depth}")
                        await self._trigger_alert("high_queue_depth", {
                            "queue_name": queue_name,
                            "depth": depth
                        })
                    
                    # Record metric
                    self.metrics_collector.record_gauge(
                        f"queue_depth_{queue_name}", depth
                    )
                
                # Check task ages
                old_tasks = db.query(TaskModel).filter(
                    TaskModel.status == TaskStatus.QUEUED,
                    TaskModel.created_at < datetime.utcnow() - timedelta(
                        minutes=self.alert_thresholds["task_age_minutes"]
                    )
                ).count()
                
                if old_tasks > 0:
                    logger.warning(f"Found {old_tasks} old queued tasks")
                    await self._trigger_alert("old_tasks", {"count": old_tasks})
                
                db.close()
                
            except Exception as e:
                logger.error(f"Error monitoring queues: {e}")
            
            await asyncio.sleep(60)  # Check every minute
    
    async def _collect_system_metrics(self):
        """Collect system-wide metrics"""
        while self._monitoring_active:
            try:
                # System metrics
                cpu_usage = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                self.metrics_collector.record_gauge("system_cpu_usage", cpu_usage)
                self.metrics_collector.record_gauge("system_memory_usage", memory.percent)
                self.metrics_collector.record_gauge("system_disk_usage", disk.percent)
                
                # Task metrics
                db = next(get_db())
                
                # Task counts by status
                status_counts = db.query(
                    TaskModel.status,
                    func.count(TaskModel.id).label('count')
                ).group_by(TaskModel.status).all()
                
                for status, count in status_counts:
                    self.metrics_collector.record_gauge(f"tasks_{status.value}", count)
                
                # Error rate calculation
                recent_tasks = db.query(TaskModel).filter(
                    TaskModel.completed_at >= datetime.utcnow() - timedelta(hours=1)
                ).count()
                
                failed_tasks = db.query(TaskModel).filter(
                    TaskModel.status == TaskStatus.FAILED,
                    TaskModel.completed_at >= datetime.utcnow() - timedelta(hours=1)
                ).count()
                
                error_rate = failed_tasks / max(recent_tasks, 1)
                self.metrics_collector.record_gauge("error_rate", error_rate)
                
                if error_rate > self.alert_thresholds["error_rate"]:
                    await self._trigger_alert("high_error_rate", {"rate": error_rate})
                
                db.close()
                
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
            
            await asyncio.sleep(30)
    
    async def get_realtime_metrics(self) -> Dict:
        """Get current metrics for dashboard"""
        try:
            db = next(get_db())
            
            # Task statistics
            task_stats = {
                "total": db.query(TaskModel).count(),
                "queued": db.query(TaskModel).filter(TaskModel.status == TaskStatus.QUEUED).count(),
                "processing": db.query(TaskModel).filter(TaskModel.status == TaskStatus.PROCESSING).count(),
                "completed": db.query(TaskModel).filter(TaskModel.status == TaskStatus.COMPLETED).count(),
                "failed": db.query(TaskModel).filter(TaskModel.status == TaskStatus.FAILED).count(),
            }
            
            # Worker statistics
            worker_stats = {
                "total": db.query(WorkerModel).count(),
                "healthy": db.query(WorkerModel).filter(WorkerModel.is_healthy == True).count(),
                "unhealthy": db.query(WorkerModel).filter(WorkerModel.is_healthy == False).count(),
            }
            
            # Recent performance data
            recent_completed = db.query(TaskModel).filter(
                TaskModel.status == TaskStatus.COMPLETED,
                TaskModel.completed_at >= datetime.utcnow() - timedelta(hours=1)
            ).order_by(desc(TaskModel.completed_at)).limit(100).all()
            
            avg_execution_time = sum(t.execution_time or 0 for t in recent_completed) / max(len(recent_completed), 1)
            
            # Queue depths
            queue_depths = dict(db.query(
                TaskModel.queue_name,
                func.count(TaskModel.id)
            ).filter(
                TaskModel.status.in_([TaskStatus.QUEUED, TaskStatus.PROCESSING])
            ).group_by(TaskModel.queue_name).all())
            
            db.close()
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "tasks": task_stats,
                "workers": worker_stats,
                "performance": {
                    "avg_execution_time": round(avg_execution_time, 3),
                    "throughput_per_hour": len(recent_completed)
                },
                "queues": queue_depths,
                "system": {
                    "cpu_usage": psutil.cpu_percent(),
                    "memory_usage": psutil.virtual_memory().percent,
                    "disk_usage": psutil.disk_usage('/').percent
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting realtime metrics: {e}")
            return {"error": str(e)}
    
    async def _trigger_alert(self, alert_type: str, context: Dict):
        """Trigger system alert"""
        alert = {
            "type": alert_type,
            "timestamp": datetime.utcnow().isoformat(),
            "context": context,
            "severity": self._get_alert_severity(alert_type)
        }
        logger.warning(f"Alert triggered: {alert}")
        # In production, integrate with Slack, PagerDuty, etc.
    
    def _get_alert_severity(self, alert_type: str) -> str:
        severity_map = {
            "high_memory": "warning",
            "high_queue_depth": "warning", 
            "old_tasks": "warning",
            "high_error_rate": "critical"
        }
        return severity_map.get(alert_type, "info")
