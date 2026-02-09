import json
from datetime import datetime
from uuid import uuid4
import os
import logging

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self._handlers = {}
        self._processed = set()
        
    def publish(self, channel: str, event_type: str, payload: dict):
        """Publish an event - in-memory for demo (no Redis required)"""
        event = {
            'event_id': str(uuid4()),
            'timestamp': datetime.utcnow().isoformat(),
            'type': event_type,
            'payload': payload
        }
        event_key = event['event_id']
        if event_key in self._processed:
            return False
        self._processed.add(event_key)
        if len(self._processed) > 1000:
            self._processed.clear()
        if event_type in self._handlers:
            try:
                self._handlers[event_type](payload)
            except Exception as e:
                logger.error(f"Handler error: {e}")
        logger.info(f"Published event {event_type} to {channel}")
        return True
    
    def subscribe(self, channels: list):
        pass
    
    def on(self, event_type: str, handler):
        self._handlers[event_type] = handler
        
    def listen(self, handler_map: dict):
        self._handlers.update(handler_map)

event_bus = EventBus()
