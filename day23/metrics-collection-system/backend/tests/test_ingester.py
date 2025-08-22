import pytest
import asyncio
from src.core.ingestion.realtime_ingester import RealtimeIngester

@pytest.mark.asyncio
async def test_ingester_initialization():
    ingester = RealtimeIngester()
    assert ingester.metrics_buffer is not None
    assert ingester.stats["total_metrics"] == 0

@pytest.mark.asyncio
async def test_metric_ingestion():
    ingester = RealtimeIngester()
    await ingester.start()
    
    test_metric = {
        "name": "cpu_usage",
        "value": 75.5,
        "unit": "%"
    }
    
    await ingester.ingest_metric("test-agent", test_metric)
    
    assert ingester.stats["total_metrics"] == 1
    assert len(ingester.metrics_buffer) == 1
    
    await ingester.stop()

@pytest.mark.asyncio
async def test_stats_collection():
    ingester = RealtimeIngester()
    stats = ingester.get_stats()
    
    assert "total_metrics" in stats
    assert "metrics_per_second" in stats
    assert "active_agents" in stats
    assert "buffer_size" in stats
