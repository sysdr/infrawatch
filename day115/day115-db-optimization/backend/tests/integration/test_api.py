"""Integration tests — require running backend service."""
import pytest
import httpx
import os

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

@pytest.fixture
def client():
    return httpx.Client(base_url=BASE_URL, timeout=30.0)

def test_health_check(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"

def test_slow_queries_returns_list(client):
    r = client.get("/api/queries/slow")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)

def test_slow_queries_structure(client):
    r = client.get("/api/queries/slow?limit=5")
    assert r.status_code == 200
    data = r.json()
    assert len(data) <= 5
    if data:
        q = data[0]
        assert "query" in q
        assert "avg_ms" in q
        assert "calls" in q

def test_index_health_returns_list(client):
    r = client.get("/api/indexes/health")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)

def test_partition_stats_returns_partitions(client):
    r = client.get("/api/partitions/stats")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    # Should have 12 partitions for audit_events
    partitions = [p for p in data if p.get("parent_table") == "audit_events"]
    assert len(partitions) == 12

def test_partition_pruning_test(client):
    r = client.get("/api/partitions/pruning-test?start=2025-05-01&end=2025-06-01")
    assert r.status_code == 200
    data = r.json()
    assert "partitions_scanned" in data
    assert "pruning_efficiency_pct" in data
    assert data["total_partitions"] == 12
    assert data["partitions_scanned"] <= data["total_partitions"]

def test_replication_status(client):
    r = client.get("/api/replication/status")
    assert r.status_code == 200
    data = r.json()
    assert "has_replica" in data
    assert "current_router_lag_ms" in data

def test_connection_stats(client):
    r = client.get("/api/replication/connections")
    assert r.status_code == 200
    data = r.json()
    assert "total_connections" in data
    assert "max_connections" in data
    assert "utilization_pct" in data

def test_table_bloat(client):
    r = client.get("/api/maintenance/bloat")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_dashboard_summary(client):
    r = client.get("/api/dashboard/summary")
    assert r.status_code == 200
    data = r.json()
    for key in ["avg_query_latency_ms","slow_query_count","replica_lag_ms","connection_utilization_pct"]:
        assert key in data

def test_vacuum_invalid_table(client):
    r = client.post("/api/maintenance/vacuum", json={"table_name": "bad; DROP TABLE users"})
    assert r.status_code == 400

def test_vacuum_valid_table(client):
    r = client.post("/api/maintenance/vacuum", json={"table_name": "users", "analyze": True})
    assert r.status_code == 200
    assert r.json()["status"] == "completed"
