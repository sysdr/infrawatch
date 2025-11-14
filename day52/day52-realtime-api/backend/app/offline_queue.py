import asyncio
from typing import List, Dict
from datetime import datetime, timedelta
import logging
from .models import Event

logger = logging.getLogger(__name__)

class OfflineQueue:
    def __init__(self, max_age_minutes: int = 60):
        self.queues: Dict[str, List[Event]] = {}
        self.max_age = timedelta(minutes=max_age_minutes)
    
    async def enqueue_event(self, client_id: str, event: Event):
        """Add event to client's offline queue"""
        if client_id not in self.queues:
            self.queues[client_id] = []
        
        self.queues[client_id].append(event)
        logger.debug(f"Queued event for offline client {client_id}")
    
    async def get_pending_events(self, client_id: str) -> List[Event]:
        """Get and clear pending events for a client"""
        if client_id not in self.queues:
            return []
        
        events = self.queues[client_id]
        self.queues[client_id] = []
        
        logger.info(f"Retrieved {len(events)} pending events for {client_id}")
        return events
    
    async def get_queue_size(self) -> int:
        """Get total number of queued events"""
        return sum(len(queue) for queue in self.queues.values())
    
    async def process_queue(self):
        """Background task to clean old events"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                now = datetime.utcnow()
                for client_id, events in list(self.queues.items()):
                    # Remove events older than max_age
                    self.queues[client_id] = [
                        e for e in events
                        if now - e.timestamp < self.max_age
                    ]
                    
                    if not self.queues[client_id]:
                        del self.queues[client_id]
                        
            except Exception as e:
                logger.error(f"Error processing offline queue: {e}")
