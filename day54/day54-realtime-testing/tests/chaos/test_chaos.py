import pytest
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))
from app.testing.chaos_tests import ChaosTestSuite
from app.testing.concurrency_tests import ConcurrencyTestSuite

BASE_URL = "ws://localhost:8000/ws"

class TestChaos:
    @pytest.mark.asyncio
    async def test_connection_recovery(self):
        suite = ChaosTestSuite(BASE_URL)
        result = await suite.test_connection_recovery(30)
        
        assert result["passed"] == True
        
    @pytest.mark.asyncio
    async def test_message_under_load(self):
        suite = ChaosTestSuite(BASE_URL)
        result = await suite.test_message_under_load(
            client_count=50,
            messages_per_client=20
        )
        
        assert result["passed"] == True
        
    @pytest.mark.asyncio
    async def test_slow_consumer(self):
        suite = ChaosTestSuite(BASE_URL)
        result = await suite.test_slow_consumer(500)
        
        assert result["passed"] == True

class TestConcurrency:
    @pytest.mark.asyncio
    async def test_simultaneous_connections(self):
        suite = ConcurrencyTestSuite(BASE_URL)
        result = await suite.test_simultaneous_connections(50)
        
        assert result["passed"] == True
        
    @pytest.mark.asyncio
    async def test_simultaneous_messages(self):
        suite = ConcurrencyTestSuite(BASE_URL)
        result = await suite.test_simultaneous_messages(30)
        
        assert result["passed"] == True
        
    @pytest.mark.asyncio
    async def test_message_ordering(self):
        suite = ConcurrencyTestSuite(BASE_URL)
        result = await suite.test_message_ordering(50)
        
        assert result["passed"] == True
        
    @pytest.mark.asyncio
    async def test_broadcast_consistency(self):
        suite = ConcurrencyTestSuite(BASE_URL)
        result = await suite.test_broadcast_consistency(15)
        
        assert result["passed"] == True
