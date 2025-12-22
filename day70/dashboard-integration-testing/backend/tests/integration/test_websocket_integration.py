import pytest
import asyncio
import json
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket

@pytest.mark.asyncio
async def test_websocket_connection():
    """Test WebSocket connection and message flow"""
    from app.main import app
    
    client = TestClient(app)
    
    with client.websocket_connect("/ws/dashboard/test-client") as websocket:
        # Receive connection confirmation
        data = websocket.receive_json()
        assert data['type'] == 'connected'
        assert data['client_id'] == 'test-client'
        
        # Send ping
        websocket.send_json({'type': 'ping'})
        
        # Receive pong
        pong = websocket.receive_json()
        assert pong['type'] == 'pong'

@pytest.mark.asyncio
async def test_metric_batching():
    """Test that metrics are properly batched"""
    from app.main import app
    
    client = TestClient(app)
    
    with client.websocket_connect("/ws/dashboard/test-client") as websocket:
        # Skip connection message
        websocket.receive_json()
        
        # Wait for batched metrics
        received_batches = []
        timeout = 5
        start = asyncio.get_event_loop().time()
        
        while len(received_batches) < 3 and (asyncio.get_event_loop().time() - start) < timeout:
            try:
                data = websocket.receive_json(timeout=1)
                if data['type'] in ['metrics_batch', 'metrics_priority']:
                    received_batches.append(data)
            except:
                break
                
        assert len(received_batches) > 0, "Should receive at least one batch"

@pytest.mark.asyncio
async def test_load_level_change():
    """Test changing load simulation level"""
    from app.main import app
    
    client = TestClient(app)
    
    with client.websocket_connect("/ws/dashboard/test-client") as websocket:
        # Skip connection message
        websocket.receive_json()
        
        # Change load level
        websocket.send_json({'type': 'set_load', 'load': 'high'})
        
        # Receive confirmation
        response = websocket.receive_json()
        assert response['type'] == 'load_updated'
        assert response['load'] == 'high'
