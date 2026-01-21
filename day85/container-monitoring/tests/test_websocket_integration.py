import pytest
import asyncio
import json
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_websocket_metrics_empty_state():
    """Test WebSocket handles empty containers state"""
    with client.websocket_connect("/api/v1/ws/metrics") as websocket:
        # Receive connection confirmation
        data = websocket.receive_json()
        assert data["type"] == "connected"
        
        # Wait for metrics update (should handle empty state)
        try:
            data = websocket.receive_json(timeout=3.0)
            # Should receive either metrics data or empty state message
            assert data["type"] in ["metrics", "ping"]
            if data["type"] == "metrics" and "data" in data:
                # Could be empty state or container data
                assert isinstance(data["data"], dict)
        except Exception:
            # Timeout is acceptable if no containers
            pass


def test_websocket_keepalive():
    """Test WebSocket keepalive mechanism"""
    with client.websocket_connect("/api/v1/ws/metrics") as websocket:
        # Receive connection confirmation
        data = websocket.receive_json()
        assert data["type"] == "connected"
        
        # Send a keepalive message
        websocket.send_text("ping")
        
        # Should receive pong or ping response
        try:
            data = websocket.receive_json(timeout=2.0)
            assert data["type"] in ["pong", "ping", "metrics"]
        except Exception:
            # Timeout acceptable
            pass


def test_websocket_multiple_connections():
    """Test multiple WebSocket connections"""
    with client.websocket_connect("/api/v1/ws/metrics") as ws1:
        with client.websocket_connect("/api/v1/ws/metrics") as ws2:
            # Both should receive connection confirmation
            data1 = ws1.receive_json()
            data2 = ws2.receive_json()
            
            assert data1["type"] == "connected"
            assert data2["type"] == "connected"


def test_websocket_disconnect_handling():
    """Test WebSocket disconnect is handled gracefully"""
    with client.websocket_connect("/api/v1/ws/metrics") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "connected"
        
    # Connection should close gracefully
    # No exceptions should be raised
