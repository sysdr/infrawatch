import asyncio
from typing import List
from .ws_client import WebSocketTestClient

class ConcurrencyTestSuite:
    def __init__(self, base_url: str = "ws://localhost:8000/ws"):
        self.base_url = base_url
        
    async def test_simultaneous_connections(self, count: int = 100) -> dict:
        """Test many connections opening at once"""
        clients = [WebSocketTestClient(f"sim-{i}") for i in range(count)]
        
        # Connect all simultaneously
        start = asyncio.get_event_loop().time()
        results = await asyncio.gather(
            *[c.connect(self.base_url) for c in clients],
            return_exceptions=True
        )
        duration = asyncio.get_event_loop().time() - start
        
        successes = sum(1 for r in results if r is None)
        failures = count - successes
        
        # Cleanup
        await asyncio.gather(*[c.close() for c in clients])
        
        return {
            "test": "simultaneous_connections",
            "total": count,
            "successes": successes,
            "failures": failures,
            "duration_ms": duration * 1000,
            "passed": failures == 0
        }
        
    async def test_simultaneous_messages(self, client_count: int = 50) -> dict:
        """Test many clients sending messages at once"""
        clients = [WebSocketTestClient(f"msg-{i}") for i in range(client_count)]
        
        # Connect all
        await asyncio.gather(*[c.connect(self.base_url) for c in clients])
        
        # Send messages simultaneously
        barrier = asyncio.Barrier(client_count)
        
        async def send_with_barrier(client):
            await barrier.wait()
            await client.send_message(f"Sync message from {client.client_id}")
            
        start = asyncio.get_event_loop().time()
        results = await asyncio.gather(
            *[send_with_barrier(c) for c in clients],
            return_exceptions=True
        )
        duration = asyncio.get_event_loop().time() - start
        
        errors = [r for r in results if isinstance(r, Exception)]
        
        # Cleanup
        await asyncio.gather(*[c.close() for c in clients])
        
        return {
            "test": "simultaneous_messages",
            "client_count": client_count,
            "errors": len(errors),
            "duration_ms": duration * 1000,
            "passed": len(errors) == 0
        }
        
    async def test_rapid_reconnection(self, cycles: int = 10) -> dict:
        """Test rapid connect/disconnect cycles"""
        client = WebSocketTestClient("reconnect-test")
        errors = []
        
        for i in range(cycles):
            try:
                await client.connect(self.base_url)
                await client.ping()
                await asyncio.sleep(0.01)
                await client.close()
                # Reset client for next cycle
                client = WebSocketTestClient(f"reconnect-test-{i}")
            except Exception as e:
                errors.append(str(e))
                
        return {
            "test": "rapid_reconnection",
            "cycles": cycles,
            "errors": len(errors),
            "error_details": errors,
            "passed": len(errors) == 0
        }
        
    async def test_message_ordering(self, message_count: int = 100) -> dict:
        """Verify messages arrive in order"""
        client = WebSocketTestClient("order-test")
        await client.connect(self.base_url)
        
        # Send numbered messages
        for i in range(message_count):
            await client.send({
                "type": "echo",
                "content": f"msg-{i}"
            })
            
        # Collect responses
        await asyncio.sleep(1)  # Wait for processing
        
        # Check ordering
        responses = [m for m in client._received_messages 
                    if m.get("type") == "echo_response"]
        
        in_order = True
        for i, resp in enumerate(responses):
            expected = f"msg-{i}"
            if resp.get("content") != expected:
                in_order = False
                break
                
        await client.close()
        
        return {
            "test": "message_ordering",
            "sent": message_count,
            "received": len(responses),
            "in_order": in_order,
            "passed": in_order and len(responses) == message_count
        }
        
    async def test_broadcast_consistency(self, client_count: int = 20) -> dict:
        """Verify all clients receive broadcasts"""
        clients = [WebSocketTestClient(f"broadcast-{i}") 
                  for i in range(client_count)]
        
        # Connect all
        await asyncio.gather(*[c.connect(self.base_url) for c in clients])
        await asyncio.sleep(0.5)  # Let connections stabilize
        
        # One client sends broadcast
        test_message = f"broadcast-test-{asyncio.get_event_loop().time()}"
        await clients[0].send_message(test_message)
        
        # Wait for delivery
        await asyncio.sleep(1)
        
        # Check all received
        received_count = 0
        for client in clients:
            for msg in client._received_messages:
                if (msg.get("type") == "broadcast" and 
                    msg.get("content") == test_message):
                    received_count += 1
                    break
                    
        await asyncio.gather(*[c.close() for c in clients])
        
        return {
            "test": "broadcast_consistency",
            "client_count": client_count,
            "received_broadcast": received_count,
            "passed": received_count == client_count
        }
        
    async def run_all_tests(self) -> List[dict]:
        """Run all concurrency tests"""
        results = []
        
        results.append(await self.test_simultaneous_connections())
        results.append(await self.test_simultaneous_messages())
        results.append(await self.test_rapid_reconnection())
        results.append(await self.test_message_ordering())
        results.append(await self.test_broadcast_consistency())
        
        return results
