import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_get_metrics():
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_metric_names():
    response = client.get("/api/v1/metrics/names")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
