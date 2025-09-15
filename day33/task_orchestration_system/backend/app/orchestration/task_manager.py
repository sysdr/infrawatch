import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TaskMetrics:
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    avg_execution_time: float = 0.0
    success_rate: float = 0.0

class TaskManager:
    def __init__(self):
        self.metrics = TaskMetrics()
        self.task_history: List[Dict] = []
        
    async def update_metrics(self, task_result: Dict):
        """Update task execution metrics"""
        self.metrics.total_tasks += 1
        
        if task_result['status'] == 'completed':
            self.metrics.completed_tasks += 1
        elif task_result['status'] == 'failed':
            self.metrics.failed_tasks += 1
            
        self.metrics.success_rate = self.metrics.completed_tasks / self.metrics.total_tasks if self.metrics.total_tasks > 0 else 0
        
        # Store in history
        self.task_history.append({
            'timestamp': datetime.now().isoformat(),
            'task_id': task_result.get('task_id'),
            'status': task_result['status'],
            'execution_time': task_result.get('execution_time', 0)
        })
        
        # Keep only last 100 entries
        if len(self.task_history) > 100:
            self.task_history = self.task_history[-100:]
    
    def get_metrics(self) -> Dict:
        """Get current task metrics"""
        return {
            'total_tasks': self.metrics.total_tasks,
            'completed_tasks': self.metrics.completed_tasks,
            'failed_tasks': self.metrics.failed_tasks,
            'success_rate': round(self.metrics.success_rate * 100, 2),
            'recent_history': self.task_history[-10:]  # Last 10 tasks
        }
