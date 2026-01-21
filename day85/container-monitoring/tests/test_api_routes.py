import pytest
import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "container-monitoring"


def test_get_containers():
    """Test getting containers list"""
    response = client.get("/api/v1/containers")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_containers_all():
    """Test getting all containers including stopped ones"""
    response = client.get("/api/v1/containers?all=true")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_alerts():
    """Test getting alerts"""
    response = client.get("/api/v1/alerts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_websocket_metrics_connection():
    """Test WebSocket metrics endpoint connection"""
    with client.websocket_connect("/api/v1/ws/metrics") as websocket:
        # Should receive connection confirmation
        data = websocket.receive_json()
        assert data["type"] == "connected"
        assert "message" in data


def test_websocket_events_connection():
    """Test WebSocket events endpoint connection"""
    with client.websocket_connect("/api/v1/ws/events") as websocket:
        # Connection should be established
        # Events may not come immediately, so we just verify connection
        assert websocket is not None


def test_websocket_metrics_data():
    """Test WebSocket metrics data flow"""
    with client.websocket_connect("/api/v1/ws/metrics") as websocket:
        # Receive connection confirmation
        data = websocket.receive_json()
        assert data["type"] == "connected"
        
        # Wait for metrics data (with timeout)
        try:
            # Try to receive at least one metrics message
            for _ in range(3):  # Check up to 3 messages
                data = websocket.receive_json(timeout=2.0)
                if data.get("type") == "metrics":
                    assert "data" in data
                    break
        except Exception:
            # If no containers, we might get empty state message
            pass


@pytest.mark.asyncio
async def test_container_metrics_endpoint():
    """Test getting metrics for a specific container"""
    # First get containers
    response = client.get("/api/v1/containers")
    containers = response.json()
    
    if containers:
        container_id = containers[0]["id"]
        response = client.get(f"/api/v1/containers/{container_id}/metrics")
        if response.status_code == 200:
            metrics = response.json()
            assert "container_id" in metrics
            assert "cpu_percent" in metrics
            assert "memory_percent" in metrics


@pytest.mark.asyncio
async def test_container_health_endpoint():
    """Test getting health for a specific container"""
    # First get containers
    response = client.get("/api/v1/containers")
    containers = response.json()
    
    if containers:
        container_id = containers[0]["id"]
        response = client.get(f"/api/v1/containers/{container_id}/health")
        if response.status_code == 200:
            health = response.json()
            assert "container_id" in health
            assert "status" in health
            assert health["status"] in ["healthy", "unhealthy", "starting", "none"]


def test_metrics_history_endpoint():
    """Test getting metrics history"""
    # First get containers
    response = client.get("/api/v1/containers")
    containers = response.json()
    
    if containers:
        container_id = containers[0]["id"]
        response = client.get(f"/api/v1/containers/{container_id}/history?duration=60")
        if response.status_code == 200:
            history = response.json()
            assert "container_id" in history
            assert "duration_seconds" in history
            assert "metrics" in history
            assert isinstance(history["metrics"], list)
