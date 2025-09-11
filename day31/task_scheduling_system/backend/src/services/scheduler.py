import asyncio
from datetime import datetime
from croniter import croniter
import threading
import time

class TaskScheduler:
    def __init__(self):
        self.tasks = {}
        self.running = False
        self.thread = None
    
    def add_task(self, task):
        """Add a task to the scheduler"""
        self.tasks[task.id] = task
        if self.running:
            self._schedule_task(task)
    
    def update_task(self, task):
        """Update a task in the scheduler"""
        self.tasks[task.id] = task
        if self.running:
            self._schedule_task(task)
    
    def remove_task(self, task_id):
        """Remove a task from the scheduler"""
        if task_id in self.tasks:
            del self.tasks[task_id]
    
    def start(self):
        """Start the scheduler"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_scheduler)
            self.thread.daemon = True
            self.thread.start()
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.thread:
            self.thread.join()
    
    def _run_scheduler(self):
        """Main scheduler loop"""
        while self.running:
            try:
                current_time = datetime.utcnow()
                
                for task_id, task in self.tasks.items():
                    if not task.is_active:
                        continue
                    
                    try:
                        cron = croniter(task.cron_expression, current_time)
                        next_run = cron.get_next(datetime)
                        
                        # Check if task should run now
                        if next_run <= current_time:
                            self._execute_task(task)
                    except Exception as e:
                        print(f"Error scheduling task {task_id}: {e}")
                
                time.sleep(1)  # Check every second
            except Exception as e:
                print(f"Scheduler error: {e}")
                time.sleep(5)
    
    def _schedule_task(self, task):
        """Schedule a specific task"""
        # This is a simplified implementation
        # In a real system, you'd use a proper job queue
        pass
    
    def _execute_task(self, task):
        """Execute a task"""
        print(f"Executing task: {task.name} (ID: {task.id})")
        # In a real system, this would queue the task for execution
        # For now, we'll just log it

# Singleton instance
scheduler = TaskScheduler()
