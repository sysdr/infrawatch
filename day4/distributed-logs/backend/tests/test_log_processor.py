"""
Unit tests for the distributed log processor.
These tests ensure reliability in production environments.
"""

import pytest
from datetime import datetime
import json
from backend.src.log_processor import LogEvent, LogLevel, DistributedLogProcessor


class TestLogEvent:
    """Test cases for LogEvent class."""
    
    def test_log_event_creation_success(self) -> None:
        """Test successful log event creation with valid data."""
        timestamp = datetime.now()
        event = LogEvent(
            timestamp=timestamp,
            level=LogLevel.INFO,
            message="Test message",
            service="test-service"
        )
        
        assert event.level == LogLevel.INFO
        assert event.message == "Test message"
        assert event.service == "test-service"
        assert event.timestamp == timestamp
        assert event.metadata == {}
    
    def test_log_event_with_metadata(self) -> None:
        """Test log event creation with metadata."""
        metadata = {"user_id": "12345", "request_id": "abcdef"}
        event = LogEvent(
            timestamp=datetime.now(),
            level=LogLevel.ERROR,
            message="Database error",
            service="user-service",
            metadata=metadata
        )
        
        assert event.metadata == metadata
    
    def test_log_event_empty_message_raises_error(self) -> None:
        """Test that empty message raises ValueError."""
        with pytest.raises(ValueError, match="Log message cannot be empty"):
            LogEvent(
                timestamp=datetime.now(),
                level=LogLevel.INFO,
                message="",
                service="test-service"
            )
    
    def test_log_event_to_dict(self) -> None:
        """Test conversion of log event to dictionary."""
        timestamp = datetime.now()
        event = LogEvent(
            timestamp=timestamp,
            level=LogLevel.WARNING,
            message="Test warning",
            service="api-service"
        )
        
        result = event.to_dict()
        
        assert result["timestamp"] == timestamp.isoformat()
        assert result["level"] == "WARNING"
        assert result["message"] == "Test warning"
        assert result["service"] == "api-service"


class TestDistributedLogProcessor:
    """Test cases for DistributedLogProcessor class."""
    
    def test_processor_initialization(self) -> None:
        """Test processor initializes with correct defaults."""
        processor = DistributedLogProcessor()
        
        assert processor.buffer_size == 1000
        assert processor.processed_count == 0
        assert processor.error_count == 0
        assert len(processor.event_buffer) == 0
    
    def test_process_valid_json_event(self) -> None:
        """Test processing of valid JSON log event."""
        processor = DistributedLogProcessor()
        
        raw_event = json.dumps({
            "timestamp": "2024-01-01T10:00:00",
            "level": "ERROR",
            "message": "Database connection failed",
            "service": "user-api",
            "metadata": {"retry_count": 3}
        })
        
        processed_event = processor.process_event(raw_event)
        
        assert processed_event is not None
        assert processed_event.level == LogLevel.ERROR
        assert processed_event.message == "Database connection failed"
        assert processed_event.service == "user-api"
        assert processed_event.metadata["retry_count"] == 3
        assert processor.processed_count == 1
    
    def test_process_invalid_json_returns_none(self) -> None:
        """Test that invalid JSON returns None and increments error count."""
        processor = DistributedLogProcessor()
        
        invalid_json = "{ invalid json }"
        result = processor.process_event(invalid_json)
        
        assert result is None
        assert processor.error_count == 1
        assert processor.processed_count == 0
    
    def test_process_missing_required_field(self) -> None:
        """Test handling of events missing required fields."""
        processor = DistributedLogProcessor()
        
        incomplete_event = json.dumps({
            "timestamp": "2024-01-01T10:00:00",
            "level": "INFO",
            # Missing 'message' and 'service'
        })
        
        result = processor.process_event(incomplete_event)
        
        assert result is None
        assert processor.error_count == 1
    
    def test_buffer_overflow_handling(self) -> None:
        """Test that buffer overflow is handled correctly."""
        processor = DistributedLogProcessor(buffer_size=2)
        
        # Add 3 events to a buffer of size 2
        for i in range(3):
            event = json.dumps({
                "timestamp": "2024-01-01T10:00:00",
                "level": "INFO",
                "message": f"Message {i}",
                "service": "test-service"
            })
            processor.process_event(event)
        
        # Should only have 2 events (latest ones)
        assert len(processor.event_buffer) == 2
        assert processor.processed_count == 3
    
    def test_get_stats(self) -> None:
        """Test statistics reporting."""
        processor = DistributedLogProcessor()
        
        # Process some valid and invalid events
        valid_event = json.dumps({
            "timestamp": "2024-01-01T10:00:00",
            "level": "INFO",
            "message": "Valid message",
            "service": "test-service"
        })
        processor.process_event(valid_event)
        processor.process_event("invalid json")
        
        stats = processor.get_stats()
        
        assert stats["processed_count"] == 1
        assert stats["error_count"] == 1
        assert stats["buffer_size"] == 1
        assert stats["success_rate"] == 50.0
