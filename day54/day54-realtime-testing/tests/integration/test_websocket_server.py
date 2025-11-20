import pytest
import asyncio
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))
from app.testing.ws_client import WebSocketTestClient

BASE_URL = "ws://localhost:8000/ws"

@pytest.fixture
async def client():
    """Create and cleanup test client"""
    c = WebSocketTestClient("integration-test")
    yield c
    if c.connected:
        await c.close()

class TestWebSocketIntegration:
    @pytest.mark.asyncio
    async def test_connection(self, client):
        await client.connect(BASE_URL)
        assert client.connected == True
        assert client.metrics.connection_time_ms > 0
        
    @pytest.mark.asyncio
    async def test_ping_pong(self, client):
        await client.connect(BASE_URL)
        await client.ping()
        await asyncio.sleep(0.5)
        
        # Should have recorded latency
        assert len(client.metrics.latencies) > 0
        assert client.metrics.latencies[0] > 0
        
    @pytest.mark.asyncio
    async def test_message_send(self, client):
        await client.connect(BASE_URL)
        await client.send_message("Hello, World!")
        
        assert client.metrics.messages_sent == 1
        assert client.metrics.bytes_sent > 0
        
    @pytest.mark.asyncio
    async def test_echo(self, client):
        await client.connect(BASE_URL)
        await client.send({
            "type": "echo",
            "content": "test-echo"
        })
        
        await asyncio.sleep(0.5)
        
        # Find echo response
        echo_responses = [m for m in client._received_messages 
                        if m.get("type") == "echo_response"]
        assert len(echo_responses) > 0
        assert echo_responses[0]["content"] == "test-echo"
        
    @pytest.mark.asyncio
    async def test_multiple_clients(self):
        clients = [WebSocketTestClient(f"multi-{i}") for i in range(5)]
        
        # Connect all
        for c in clients:
            await c.connect(BASE_URL)
            
        # Verify all connected
        for c in clients:
            assert c.connected == True
            
        # Cleanup
        for c in clients:
            await c.close()
            
    @pytest.mark.asyncio
    async def test_reconnection(self, client):
        await client.connect(BASE_URL)
        await client.close()
        
        # Create new client with same logic
        client2 = WebSocketTestClient("reconnect-test")
        await client2.connect(BASE_URL)
        
        assert client2.connected == True
        await client2.close()
