import pytest
import asyncio
from datetime import datetime, timedelta
from backend.app.aggregation.engine import AggregationEngine, TimeWindow
from backend.app.models.metrics import MetricData

@pytest.mark.asyncio
async def test_time_window():
    """Test time window functionality"""
    window = TimeWindow(window_size=timedelta(minutes=5))
    
    # Add test data
    metric = MetricData(
        name="test_metric",
        value=50.0,
        timestamp=datetime.utcnow(),
        tags={"server": "test"}
    )
    
    window.add_point(metric)
    aggregations = window.get_aggregations()
    
    assert aggregations["count"] == 1
    assert aggregations["average"] == 50.0
    assert aggregations["min"] == 50.0
    assert aggregations["max"] == 50.0

@pytest.mark.asyncio
async def test_aggregation_engine():
    """Test aggregation engine processing"""
    engine = AggregationEngine()
    
    # Process test metric
    metric = MetricData(
        name="cpu_usage",
        value=75.5,
        timestamp=datetime.utcnow(),
        tags={"server": "web-1"}
    )
    
    await engine.process_metric(metric)
    aggregations = await engine.get_current_aggregations()
    
    assert len(aggregations) == 1
    assert aggregations[0]["metric_name"] == "cpu_usage"
    assert aggregations[0]["aggregations"]["average"] == 75.5

@pytest.mark.asyncio
async def test_multiple_metrics():
    """Test processing multiple metrics"""
    engine = AggregationEngine()
    
    # Process multiple metrics
    metrics = [
        MetricData(name="cpu_usage", value=50.0, timestamp=datetime.utcnow(), tags={"server": "web-1"}),
        MetricData(name="cpu_usage", value=60.0, timestamp=datetime.utcnow(), tags={"server": "web-1"}),
        MetricData(name="memory_usage", value=80.0, timestamp=datetime.utcnow(), tags={"server": "web-1"}),
    ]
    
    for metric in metrics:
        await engine.process_metric(metric)
    
    aggregations = await engine.get_current_aggregations()
    
    # Should have 2 different metric types
    metric_names = {agg["metric_name"] for agg in aggregations}
    assert "cpu_usage" in metric_names
    assert "memory_usage" in metric_names

def test_window_key_creation():
    """Test window key creation"""
    engine = AggregationEngine()
    
    metric = MetricData(
        name="test_metric",
        value=100.0,
        timestamp=datetime.utcnow(),
        tags={"server": "web-1", "env": "prod"}
    )
    
    key = engine._create_window_key(metric)
    assert "test_metric" in key
    assert "server:web-1" in key
    assert "env:prod" in key

if __name__ == "__main__":
    pytest.main([__file__])
