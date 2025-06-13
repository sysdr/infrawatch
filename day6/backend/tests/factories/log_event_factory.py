import factory
from factory import Faker
from datetime import datetime, timedelta
import json
import random
from src.models.log_event import LogEvent, LogLevel

class LogEventFactory(factory.Factory):
    class Meta:
        model = LogEvent
    
    id = factory.Sequence(lambda n: n)
    message = Faker('sentence', nb_words=6)
    level = factory.Iterator(LogLevel)
    timestamp = factory.LazyFunction(datetime.utcnow)
    source = Faker('word')
    metadata = factory.LazyFunction(lambda: json.dumps({"user_id": random.randint(1, 1000)}))
    
    @classmethod
    def create_batch_with_timestamps(cls, size=10, start_time=None, interval_seconds=60):
        """Create batch of logs with specific timestamp intervals."""
        if start_time is None:
            start_time = datetime.utcnow() - timedelta(hours=1)
        
        logs = []
        for i in range(size):
            timestamp = start_time + timedelta(seconds=i * interval_seconds)
            logs.append(cls.build(timestamp=timestamp))
        return logs
    
    @classmethod
    def create_error_scenario(cls, error_count=5, normal_count=10):
        """Create realistic error scenario with burst of errors."""
        logs = []
        
        # Normal logs first
        for _ in range(normal_count):
            logs.append(cls.build(level=LogLevel.INFO))
        
        # Then error burst
        error_start = datetime.utcnow()
        for i in range(error_count):
            timestamp = error_start + timedelta(seconds=i * 5)
            logs.append(cls.build(
                level=LogLevel.ERROR,
                message=f"Database connection failed (attempt {i+1})",
                timestamp=timestamp
            ))
        
        return logs
    
    @classmethod
    def create_high_volume_simulation(cls, events_per_minute=100, duration_minutes=1):
        """Simulate high-volume log generation."""
        total_events = events_per_minute * duration_minutes
        interval_seconds = 60 / events_per_minute
        
        return cls.create_batch_with_timestamps(
            size=total_events,
            interval_seconds=interval_seconds
        )
