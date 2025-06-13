import pytest
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.log_event import LogEvent, LogLevel
from tests.factories.log_event_factory import LogEventFactory

@pytest.mark.integration
class TestLogEventDatabase:
    async def test_store_single_log_event(self, test_session: AsyncSession):
        """Test storing a single log event."""
        event = LogEvent(
            message="Integration test message",
            level=LogLevel.INFO,
            source="integration_test"
        )
        
        test_session.add(event)
        await test_session.commit()
        await test_session.refresh(event)
        
        assert event.id is not None
        assert event.message == "Integration test message"
    
    async def test_retrieve_log_events(self, test_session: AsyncSession):
        """Test retrieving log events from database."""
        # Create test events
        events = [
            LogEvent(message=f"Test {i}", level=LogLevel.INFO)
            for i in range(3)
        ]
        
        for event in events:
            test_session.add(event)
        await test_session.commit()
        
        # Retrieve events
        result = await test_session.execute(select(LogEvent))
        stored_events = result.scalars().all()
        
        assert len(stored_events) >= 3
        messages = [event.message for event in stored_events]
        assert "Test 0" in messages
        assert "Test 1" in messages
        assert "Test 2" in messages
    
    async def test_concurrent_log_storage(self, test_session: AsyncSession):
        """Test handling concurrent log writes."""
        async def store_log(session, message):
            event = LogEvent(message=message, level=LogLevel.INFO)
            session.add(event)
            await session.commit()
            await session.refresh(event)
            return event.id
        
        # Create multiple concurrent tasks
        tasks = [
            store_log(test_session, f"Concurrent log {i}")
            for i in range(5)
        ]
        
        # Execute concurrently
        event_ids = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify all succeeded and got unique IDs
        assert len(event_ids) == 5
        assert all(isinstance(id_val, int) for id_val in event_ids)
        assert len(set(event_ids)) == 5  # All unique
    
    @pytest.mark.slow
    async def test_high_volume_log_processing(self, test_session: AsyncSession):
        """Test system behavior under high load."""
        import time
        
        # Generate realistic high-volume scenario
        events = LogEventFactory.create_high_volume_simulation(
            events_per_minute=100, 
            duration_minutes=1
        )
        
        start_time = time.time()
        
        for event in events:
            test_session.add(event)
        
        await test_session.commit()
        duration = time.time() - start_time
        
        # Verify performance and data integrity
        assert duration < 10  # Should process 100 logs quickly
        
        # Count stored events
        result = await test_session.execute(select(LogEvent))
        stored_count = len(result.scalars().all())
        assert stored_count >= 100
