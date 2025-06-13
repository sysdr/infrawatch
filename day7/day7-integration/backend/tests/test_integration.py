import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "Day 7 Integration API is running!" in response.json()["message"]

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "system" in data
    assert "application" in data

def test_hello_world():
    response = client.get("/api/hello")
    assert response.status_code == 200
    data = response.json()
    assert "Hello from the backend!" in data["message"]
    assert "timestamp" in data
    assert "count" in data

def test_echo_endpoint():
    test_data = {"test": "data", "number": 123}
    response = client.post("/api/echo", json=test_data)
    assert response.status_code == 200
    data = response.json()
    assert data["echo"] == test_data

def test_status_endpoint():
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["application"] == "Day 7 Integration Demo"
    assert "metrics" in data
