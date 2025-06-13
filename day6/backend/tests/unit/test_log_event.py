import pytest
from datetime import datetime
from src.models.log_event import LogEvent, LogLevel
from tests.factories.log_event_factory import LogEventFactory

class TestLogEvent:
    def test_log_event_creation(self):
        """Test basic log event creation."""
        event = LogEvent(
            message="Test message",
            level=LogLevel.INFO,
            source="test_app"
        )
        
        assert event.message == "Test message"
        assert event.level == LogLevel.INFO
        assert event.source == "test_app"
    
    def test_log_event_representation(self):
        """Test string representation of log event."""
        event = LogEvent(id=1, message="A" * 100, level=LogLevel.ERROR)
        repr_str = repr(event)
        
        assert "LogEvent(id=1" in repr_str
        assert "ERROR" in repr_str
        assert len(repr_str) < 150  # Should be truncated
    
    @pytest.mark.parametrize("level", [
        LogLevel.DEBUG,
        LogLevel.INFO,
        LogLevel.WARNING,
        LogLevel.ERROR,
        LogLevel.CRITICAL
    ])
    def test_all_log_levels(self, level):
        """Test all log levels are valid."""
        event = LogEvent(message="Test", level=level)
        assert event.level == level

class TestLogEventFactory:
    def test_create_single_log(self):
        """Test factory creates valid log event."""
        event = LogEventFactory.build()
        
        assert isinstance(event.message, str)
        assert event.level in LogLevel
        assert isinstance(event.timestamp, datetime)
    
    def test_create_batch(self):
        """Test factory creates multiple events."""
        events = LogEventFactory.build_batch(5)
        
        assert len(events) == 5
        assert all(isinstance(event.message, str) for event in events)
    
    def test_error_scenario_generation(self):
        """Test realistic error scenario generation."""
        logs = LogEventFactory.create_error_scenario(error_count=3, normal_count=5)
        
        assert len(logs) == 8
        
        # Check we have both normal and error logs
        levels = [log.level for log in logs]
        assert LogLevel.INFO in levels
        assert LogLevel.ERROR in levels
        
        # Error logs should have descriptive messages
        error_logs = [log for log in logs if log.level == LogLevel.ERROR]
        assert len(error_logs) == 3
        assert all("Database connection failed" in log.message for log in error_logs)
    
    def test_high_volume_simulation(self):
        """Test high-volume log generation."""
        logs = LogEventFactory.create_high_volume_simulation(
            events_per_minute=60, 
            duration_minutes=1
        )
        
        assert len(logs) == 60
        
        # Check timestamps are properly spaced
        timestamps = [log.timestamp for log in logs]
        time_diffs = [(timestamps[i+1] - timestamps[i]).total_seconds() 
                     for i in range(len(timestamps)-1)]
        
        # Should be approximately 1 second between events (60 events/minute)
        assert all(0.8 <= diff <= 1.2 for diff in time_diffs)
