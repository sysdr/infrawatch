from typing import Dict, Optional
from datetime import datetime
import logging
from .models import Event

logger = logging.getLogger(__name__)

class SyncEngine:
    def __init__(self):
        self.client_states: Dict[str, Dict] = {}
        self.version_vectors: Dict[str, int] = {}
        self.conflict_count = 0
        self.resolved_count = 0
    
    def update_state(self, client_id: str, event: Event):
        """Update client state with new event"""
        if client_id not in self.client_states:
            self.client_states[client_id] = {}
        
        # Update version vector
        self.version_vectors[client_id] = event.version
        
        # Update state
        entity_id = event.payload.get("entity_id", "default")
        self.client_states[client_id][entity_id] = {
            "data": event.payload,
            "version": event.version,
            "timestamp": event.timestamp
        }
        
        logger.debug(f"Updated state for {client_id}: version {event.version}")
    
    def detect_conflict(self, event: Event) -> Optional[Event]:
        """Detect if event conflicts with existing state"""
        entity_id = event.payload.get("entity_id", "default")
        
        # Check all clients for conflicts (including same client for version conflicts)
        for client_id, state in self.client_states.items():
            if entity_id in state:
                existing = state[entity_id]
                
                # Version conflict detected: existing version >= new version
                # This catches: outdated versions, duplicate versions, or same client sending same version
                if existing["version"] >= event.version:
                    self.conflict_count += 1
                    logger.warning(
                        f"Conflict detected: entity {entity_id}, "
                        f"existing v{existing['version']} vs new v{event.version} "
                        f"(client: {client_id} vs {event.client_id})"
                    )
                    return Event(
                        type=event.type,
                        payload=existing["data"],
                        client_id=client_id,
                        version=existing["version"],
                        timestamp=existing["timestamp"]
                    )
        
        return None
    
    def resolve_conflict(self, new_event: Event, existing_event: Event) -> Event:
        """Resolve conflict using last-write-wins strategy"""
        self.resolved_count += 1
        
        # Last write wins based on timestamp
        if new_event.timestamp > existing_event.timestamp:
            logger.info("Conflict resolved: accepting newer event")
            # Increment version
            new_event.version = existing_event.version + 1
            return new_event
        else:
            logger.info("Conflict resolved: keeping existing event")
            return existing_event
    
    def get_client_state(self, client_id: str) -> Dict:
        """Get current state for a client"""
        return self.client_states.get(client_id, {})
    
    def get_conflict_count(self) -> int:
        return self.conflict_count
    
    def get_resolved_count(self) -> int:
        return self.resolved_count
