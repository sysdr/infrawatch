import random
from datetime import datetime, timedelta

class LoadBalancer:
    def __init__(self):
        self.workers = {}
        self.worker_weights = {}
        self.last_assignment = {}
    
    def add_worker(self, worker_id, max_tasks=5, specializations=None):
        """Add a worker to the load balancer"""
        self.workers[worker_id] = {
            'max_tasks': max_tasks,
            'current_tasks': 0,
            'specializations': specializations or [],
            'last_heartbeat': datetime.utcnow()
        }
        self.worker_weights[worker_id] = 1.0
    
    def remove_worker(self, worker_id):
        """Remove a worker from the load balancer"""
        if worker_id in self.workers:
            del self.workers[worker_id]
        if worker_id in self.worker_weights:
            del self.worker_weights[worker_id]
    
    def get_available_worker(self, task_requirements=None):
        """Get an available worker for a task"""
        available_workers = []
        
        for worker_id, worker in self.workers.items():
            if worker['current_tasks'] < worker['max_tasks']:
                # Check if worker has required specializations
                if task_requirements and worker['specializations']:
                    if not any(req in worker['specializations'] for req in task_requirements):
                        continue
                
                available_workers.append(worker_id)
        
        if not available_workers:
            return None
        
        # Use weighted random selection
        weights = [self.worker_weights.get(wid, 1.0) for wid in available_workers]
        return random.choices(available_workers, weights=weights)[0]
    
    def assign_task(self, worker_id, task_id):
        """Assign a task to a worker"""
        if worker_id in self.workers:
            self.workers[worker_id]['current_tasks'] += 1
            self.last_assignment[worker_id] = datetime.utcnow()
    
    def complete_task(self, worker_id, task_id):
        """Mark a task as completed"""
        if worker_id in self.workers:
            self.workers[worker_id]['current_tasks'] = max(0, self.workers[worker_id]['current_tasks'] - 1)
    
    def update_worker_health(self, worker_id, is_healthy):
        """Update worker health status"""
        if worker_id in self.worker_weights:
            if is_healthy:
                self.worker_weights[worker_id] = min(1.0, self.worker_weights[worker_id] + 0.1)
            else:
                self.worker_weights[worker_id] = max(0.1, self.worker_weights[worker_id] - 0.2)
