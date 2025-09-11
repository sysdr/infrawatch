import heapq
from datetime import datetime

class PriorityQueue:
    def __init__(self):
        self.queue = []
        self.counter = 0
    
    def enqueue(self, task, priority=None):
        """Add a task to the priority queue"""
        if priority is None:
            priority = task.priority
        
        # Use counter to maintain FIFO order for same priority
        heapq.heappush(self.queue, (-priority, self.counter, task))
        self.counter += 1
    
    def dequeue(self):
        """Remove and return the highest priority task"""
        if not self.queue:
            return None
        
        priority, counter, task = heapq.heappop(self.queue)
        return task
    
    def peek(self):
        """Return the highest priority task without removing it"""
        if not self.queue:
            return None
        
        priority, counter, task = self.queue[0]
        return task
    
    def size(self):
        """Return the number of tasks in the queue"""
        return len(self.queue)
    
    def is_empty(self):
        """Check if the queue is empty"""
        return len(self.queue) == 0
