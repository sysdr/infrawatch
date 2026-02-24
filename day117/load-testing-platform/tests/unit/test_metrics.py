import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

def test_system_metrics_keys():
    from app.services.metrics import collect_system_metrics
    m = collect_system_metrics()
    assert "cpu_percent" in m
    assert "memory_percent" in m
    assert "timestamp" in m
    assert 0 <= m["cpu_percent"] <= 100
    assert 0 <= m["memory_percent"] <= 100

def test_system_metrics_types():
    from app.services.metrics import collect_system_metrics
    m = collect_system_metrics()
    assert isinstance(m["cpu_percent"], float)
    assert isinstance(m["memory_percent"], float)
    assert isinstance(m["memory_used_mb"], float)
