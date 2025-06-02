"""
Distributed Log Processing System - Core Processor
This module handles log event processing in a distributed environment.
Used by industry leaders for real-time log analytics.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import logging
from enum import Enum


class LogLevel(Enum):
    """Enumeration of supported log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogEvent:
    """Represents a structured log event in our distributed system."""
    
    def __init__(
        self, 
        timestamp: datetime, 
        level: LogLevel, 
        message: str,
        service: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize a log event with validation."""
        self.timestamp = timestamp
        self.level = level
        self.message = message
        self.service = service
        self.metadata = metadata or {}
        
        # Validate required fields
        if not message.strip():
            raise ValueError("Log message cannot be empty")
        if not service.strip():
            raise ValueError("Service name cannot be empty")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert log event to dictionary for storage/transmission."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "message": self.message,
            "service": self.service,
            "metadata": self.metadata
        }


class DistributedLogProcessor:
    """
    Main processor for handling log events across multiple services.
    Designed for high-throughput distributed systems.
    """
    
    def __init__(self, buffer_size: int = 1000) -> None:
        """Initialize the processor with configurable buffer size."""
        self.buffer_size = buffer_size
        self.event_buffer: List[LogEvent] = []
        self.processed_count = 0
        self.error_count = 0
        self.logger = logging.getLogger(__name__)
    
    def process_event(self, raw_event: str) -> Optional[LogEvent]:
        """
        Process a raw log string into a structured LogEvent.
        
        Args:
            raw_event: JSON string containing log data
            
        Returns:
            LogEvent if successful, None if processing fails
        """
        try:
            # Parse JSON - this is where type safety becomes critical
            event_data = json.loads(raw_event)
            
            # Validate required fields
            required_fields = ["timestamp", "level", "message", "service"]
            for field in required_fields:
                if field not in event_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Parse timestamp with error handling
            try:
                timestamp = datetime.fromisoformat(event_data["timestamp"])
            except ValueError:
                # Fallback to current time if timestamp is invalid
                timestamp = datetime.now()
                self.logger.warning(f"Invalid timestamp in event, using current time")
            
            # Validate and convert log level
            try:
                level = LogLevel(event_data["level"].upper())
            except ValueError:
                level = LogLevel.INFO
                self.logger.warning(f"Invalid log level: {event_data['level']}, defaulting to INFO")
            
            # Create structured event
            event = LogEvent(
                timestamp=timestamp,
                level=level,
                message=event_data["message"],
                service=event_data["service"],
                metadata=event_data.get("metadata")
            )
            
            # Add to buffer with overflow protection
            if len(self.event_buffer) >= self.buffer_size:
                self.event_buffer.pop(0)  # Remove oldest event
            
            self.event_buffer.append(event)
            self.processed_count += 1
            
            return event
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            self.error_count += 1
            self.logger.error(f"Error processing event: {e}")
            return None
    
    def get_stats(self) -> Dict[str, int]:
        """Get processing statistics."""
        return {
            "processed_count": self.processed_count,
            "error_count": self.error_count,
            "buffer_size": len(self.event_buffer),
            "success_rate": (
                self.processed_count / (self.processed_count + self.error_count) * 100
                if (self.processed_count + self.error_count) > 0 else 0
            )
        }
    
    def flush_buffer(self) -> List[LogEvent]:
        """Flush and return all buffered events."""
        events = self.event_buffer.copy()
        self.event_buffer.clear()
        return events
