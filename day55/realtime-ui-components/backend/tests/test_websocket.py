import pytest
from fastapi.testclient import TestClient
from app.main import app
import json

@pytest.fixture
def client():
    return TestClient(app)

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "connections" in data

def test_stats_endpoint(client):
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert "user_count" in data
    assert "message_rate" in data
    assert "timestamp" in data

def test_websocket_connection(client):
    with client.websocket_connect("/ws") as websocket:
        # Receive connection message
        data = websocket.receive_json()
        assert data["type"] == "connection"
        assert data["data"]["status"] == "connected"

def test_websocket_ping_pong(client):
    with client.websocket_connect("/ws") as websocket:
        # Skip connection message
        websocket.receive_json()
        
        # Send ping
        websocket.send_json({
            "type": "ping",
            "data": {"client_timestamp": 1000}
        })
        
        # Receive pong
        response = websocket.receive_json()
        assert response["type"] == "pong"

def test_websocket_message_ack(client):
    with client.websocket_connect("/ws") as websocket:
        # Skip connection message
        websocket.receive_json()
        
        # Send message
        websocket.send_json({
            "type": "message",
            "data": {"id": "test-123", "content": "Hello"}
        })
        
        # Receive acknowledgment
        response = websocket.receive_json()
        assert response["type"] == "message_ack"
        assert response["data"]["id"] == "test-123"
        assert response["data"]["status"] == "delivered"
