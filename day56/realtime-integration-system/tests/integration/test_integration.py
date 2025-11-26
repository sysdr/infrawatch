import pytest
import asyncio
import websockets
import json
import httpx

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"

@pytest.mark.asyncio
async def test_health_check():
    """Test health endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/health/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

@pytest.mark.asyncio
async def test_websocket_connection():
    """Test WebSocket connection"""
    client_id = "test_client"
    uri = f"{WS_URL}/ws/{client_id}"
    
    async with websockets.connect(uri) as websocket:
        # Wait for connection message
        message = await websocket.recv()
        data = json.loads(message)
        
        assert data["type"] == "connected"
        assert data["client_id"] == client_id

@pytest.mark.asyncio
async def test_notification_flow():
    """Test end-to-end notification flow"""
    client_id = "test_client_notif"
    uri = f"{WS_URL}/ws/{client_id}"
    
    async with websockets.connect(uri) as websocket:
        # Wait for connection
        await websocket.recv()
        
        # Send notification request
        await websocket.send(json.dumps({
            "type": "send_notification",
            "notification_data": {
                "channel": "email",
                "priority": "normal",
                "message": "Test notification"
            }
        }))
        
        # Wait for response
        message = await websocket.recv()
        data = json.loads(message)
        
        assert data["type"] == "notification_sent"
        assert data["result"]["status"] == "sent"

@pytest.mark.asyncio
async def test_alert_creation():
    """Test alert creation and broadcast"""
    client_id_1 = "test_client_alert_1"
    client_id_2 = "test_client_alert_2"
    
    # Connect two clients
    async with websockets.connect(f"{WS_URL}/ws/{client_id_1}") as ws1:
        async with websockets.connect(f"{WS_URL}/ws/{client_id_2}") as ws2:
            # Wait for connections
            await ws1.recv()
            await ws2.recv()
            
            # Client 1 creates alert
            await ws1.send(json.dumps({
                "type": "create_alert",
                "alert_data": {
                    "severity": "high",
                    "message": "Test alert"
                }
            }))
            
            # Both clients should receive alert_created
            msg1 = await asyncio.wait_for(ws1.recv(), timeout=2.0)
            msg2 = await asyncio.wait_for(ws2.recv(), timeout=2.0)
            
            data1 = json.loads(msg1)
            data2 = json.loads(msg2)
            
            assert data1["type"] == "alert_created"
            assert data2["type"] == "alert_created"
            assert data1["alert"]["severity"] == "high"

@pytest.mark.asyncio
async def test_reconnection_state_sync():
    """Test state synchronization after reconnection"""
    client_id = "test_client_sync"
    uri = f"{WS_URL}/ws/{client_id}"
    
    # First connection
    async with websockets.connect(uri) as ws1:
        await ws1.recv()  # Connection message
        
        # Create some state changes
        await ws1.send(json.dumps({
            "type": "create_alert",
            "alert_data": {"severity": "info", "message": "State test"}
        }))
        
        await asyncio.sleep(0.5)
    
    # Reconnect and request sync
    async with websockets.connect(uri) as ws2:
        await ws2.recv()  # Connection message
        
        # Request state sync
        await ws2.send(json.dumps({
            "type": "sync_state",
            "last_version": 0
        }))
        
        message = await ws2.recv()
        data = json.loads(message)
        
        assert data["type"] == "state_sync"
        assert "delta" in data

@pytest.mark.asyncio
async def test_system_metrics():
    """Test metrics endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/health/metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert "counters" in data or "latencies" in data
