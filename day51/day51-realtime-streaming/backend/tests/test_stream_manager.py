import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from app.services.stream_manager import StreamManager

@pytest.mark.asyncio
async def test_stream_manager_connect():
    sio_mock = AsyncMock()
    manager = StreamManager(sio_mock)
    
    await manager.handle_connect('test_sid')
    assert 'test_sid' in manager.connections
    sio_mock.emit.assert_called_once()

@pytest.mark.asyncio
async def test_stream_manager_subscribe():
    sio_mock = AsyncMock()
    manager = StreamManager(sio_mock)
    
    await manager.handle_connect('test_sid')
    await manager.subscribe('test_sid', {'topics': ['metrics_update']})
    
    assert 'test_sid' in manager.subscriptions['metrics_update']

@pytest.mark.asyncio
async def test_broadcast():
    sio_mock = AsyncMock()
    manager = StreamManager(sio_mock)
    
    await manager.handle_connect('test_sid')
    await manager.subscribe('test_sid', {'topics': ['test_topic']})
    await manager.broadcast('test_topic', {'data': 'test'}, priority='critical')
    
    # Should call emit for critical messages
    await asyncio.sleep(0.1)
    assert sio_mock.emit.call_count >= 1
