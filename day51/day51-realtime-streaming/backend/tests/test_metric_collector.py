import pytest
from unittest.mock import Mock, AsyncMock
from app.services.metric_collector import MetricCollector

@pytest.mark.asyncio
async def test_collect_metrics():
    stream_manager_mock = Mock()
    collector = MetricCollector(stream_manager_mock)
    
    metrics = await collector.collect_metrics()
    
    assert 'cpu' in metrics
    assert 'memory' in metrics
    assert 'disk' in metrics
    assert 'timestamp' in metrics
    assert metrics['cpu']['percent'] >= 0

def test_significant_change():
    stream_manager_mock = Mock()
    collector = MetricCollector(stream_manager_mock)
    
    collector.last_metrics = {'cpu': {'percent': 50.0}}
    current = {'cpu': {'percent': 60.0}}
    
    assert collector._is_significant_change(current) == True
    
    current = {'cpu': {'percent': 52.0}}
    assert collector._is_significant_change(current) == False
