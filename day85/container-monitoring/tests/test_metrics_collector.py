import pytest
from datetime import datetime
from backend.services.metrics_collector import MetricsCollector
from backend.models.container import ContainerMetrics

def test_metrics_collection():
    """Test metrics collection and baseline calculation"""
    collector = MetricsCollector(window_size=100)
    
    # Add sample metrics
    for i in range(70):  # Need 60+ for baseline
        metrics = ContainerMetrics(
            container_id="test123",
            container_name="test-container",
            timestamp=datetime.utcnow(),
            cpu_percent=20.0 + (i % 10),
            cpu_delta=1000000,
            system_cpu_delta=10000000,
            memory_usage=50000000,
            memory_limit=100000000,
            memory_percent=50.0,
            memory_cache=5000000,
            network_rx_bytes=1000000,
            network_tx_bytes=500000,
            network_rx_packets=10000,
            network_tx_packets=5000,
            blkio_read=100000,
            blkio_write=50000
        )
        collector.add_metrics(metrics)
    
    # Check baseline
    baseline = collector.get_baseline("test123")
    assert baseline is not None
    assert 'cpu_mean' in baseline
    assert 'memory_mean' in baseline

def test_anomaly_detection():
    """Test anomaly detection"""
    collector = MetricsCollector()
    
    # Add normal metrics
    for i in range(70):
        metrics = ContainerMetrics(
            container_id="test123",
            container_name="test-container",
            timestamp=datetime.utcnow(),
            cpu_percent=20.0,
            cpu_delta=1000000,
            system_cpu_delta=10000000,
            memory_usage=50000000,
            memory_limit=100000000,
            memory_percent=50.0,
            memory_cache=5000000,
            network_rx_bytes=1000000,
            network_tx_bytes=500000,
            network_rx_packets=10000,
            network_tx_packets=5000,
            blkio_read=100000,
            blkio_write=50000
        )
        collector.add_metrics(metrics)
    
    # Add spike
    spike_metrics = ContainerMetrics(
        container_id="test123",
        container_name="test-container",
        timestamp=datetime.utcnow(),
        cpu_percent=95.0,  # Spike
        cpu_delta=1000000,
        system_cpu_delta=10000000,
        memory_usage=50000000,
        memory_limit=100000000,
        memory_percent=50.0,
        memory_cache=5000000,
        network_rx_bytes=1000000,
        network_tx_bytes=500000,
        network_rx_packets=10000,
        network_tx_packets=5000,
        blkio_read=100000,
        blkio_write=50000
    )
    
    alerts = collector.check_anomalies(spike_metrics)
    assert len(alerts) > 0
    assert any(a.alert_type == 'cpu' for a in alerts)
