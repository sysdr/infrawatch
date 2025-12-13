import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_multi_series_endpoint():
    response = client.get("/api/charts/multi-series?metrics=cpu&metrics=memory")
    assert response.status_code == 200
    data = response.json()
    assert "series" in data
    assert len(data["series"]) == 2
    assert "metadata" in data

def test_stacked_endpoint():
    response = client.get(
        "/api/charts/stacked?categories=Q1&categories=Q2&series=sales&series=costs"
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) == 2

def test_scatter_endpoint():
    response = client.get("/api/charts/scatter?x_metric=requests&y_metric=latency")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "correlation" in data
    assert len(data["data"]) == 1000

def test_heatmap_endpoint():
    response = client.get("/api/charts/heatmap?metric=requests&days=7")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) == 168  # 7 days * 24 hours

def test_latency_distribution():
    response = client.get("/api/charts/custom/latency-distribution")
    assert response.status_code == 200
    data = response.json()
    assert "distributions" in data
    assert len(data["distributions"]) == 4

def test_status_timeline():
    response = client.get("/api/charts/custom/status-timeline?hours=24")
    assert response.status_code == 200
    data = response.json()
    assert "timeline" in data
    assert len(data["timeline"]) == 4
