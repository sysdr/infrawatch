import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))
from app.testing.ws_client import WebSocketTestClient, ConnectionMetrics

class TestConnectionMetrics:
    def test_empty_latencies(self):
        metrics = ConnectionMetrics()
        assert metrics.avg_latency == 0
        assert metrics.p95_latency == 0
        assert metrics.p99_latency == 0
        
    def test_latency_calculations(self):
        metrics = ConnectionMetrics()
        metrics.latencies = list(range(1, 101))  # 1-100ms
        
        assert metrics.avg_latency == 50.5
        assert metrics.p95_latency == 95
        assert metrics.p99_latency == 99

class TestWebSocketTestClient:
    def test_client_initialization(self):
        client = WebSocketTestClient("test-client")
        assert client.client_id == "test-client"
        assert client.connected == False
        assert client.ws is None
        
    @pytest.mark.asyncio
    async def test_metrics_tracking(self):
        client = WebSocketTestClient("metrics-test")
        
        # Simulate metrics
        client.metrics.messages_sent = 10
        client.metrics.bytes_sent = 1000
        client.metrics.latencies = [10, 20, 30]
        
        metrics = client.get_metrics()
        assert metrics.messages_sent == 10
        assert metrics.bytes_sent == 1000
        assert len(metrics.latencies) == 3
        
    def test_client_id_uniqueness(self):
        client1 = WebSocketTestClient("client-1")
        client2 = WebSocketTestClient("client-2")
        assert client1.client_id != client2.client_id
