import asyncio
import time
from typing import List, Dict
from .ws_client import WebSocketTestClient

class ChaosTestSuite:
    def __init__(self, base_url: str = "ws://localhost:8000/ws"):
        self.base_url = base_url
        
    async def test_connection_recovery(self, client_count: int = 50) -> Dict:
        """Test client reconnection after disconnection"""
        clients = [WebSocketTestClient(f"chaos-{i}") 
                  for i in range(client_count)]
        
        # Connect all
        await asyncio.gather(*[c.connect(self.base_url) for c in clients])
        
        # Simulate disconnections by closing half the clients
        half = client_count // 2
        for i in range(half):
            await clients[i].close()
            
        # Reconnect
        reconnect_errors = []
        for i in range(half):
            clients[i] = WebSocketTestClient(f"chaos-reconnect-{i}")
            try:
                await clients[i].connect(self.base_url)
            except Exception as e:
                reconnect_errors.append(str(e))
                
        # Verify all connected
        connected = sum(1 for c in clients if c.connected)
        
        # Cleanup
        await asyncio.gather(*[c.close() for c in clients])
        
        return {
            "test": "connection_recovery",
            "total": client_count,
            "disconnected": half,
            "reconnected": half - len(reconnect_errors),
            "final_connected": connected,
            "passed": connected == client_count
        }
        
    async def test_message_under_load(self, client_count: int = 100,
                                       messages_per_client: int = 50) -> Dict:
        """Test message delivery under heavy load"""
        clients = [WebSocketTestClient(f"load-{i}") 
                  for i in range(client_count)]
        
        # Connect all
        await asyncio.gather(*[c.connect(self.base_url) for c in clients])
        
        # Send many messages simultaneously
        start_time = time.time()
        send_tasks = []
        
        for client in clients:
            for j in range(messages_per_client):
                send_tasks.append(
                    client.send_message(f"msg-{client.client_id}-{j}")
                )
                
        results = await asyncio.gather(*send_tasks, return_exceptions=True)
        duration = time.time() - start_time
        
        errors = [r for r in results if isinstance(r, Exception)]
        total_messages = client_count * messages_per_client
        
        # Cleanup
        await asyncio.gather(*[c.close() for c in clients])
        
        return {
            "test": "message_under_load",
            "clients": client_count,
            "messages_per_client": messages_per_client,
            "total_messages": total_messages,
            "errors": len(errors),
            "duration_seconds": duration,
            "messages_per_second": total_messages / duration,
            "passed": len(errors) < total_messages * 0.01  # <1% error rate
        }
        
    async def test_slow_consumer(self, message_count: int = 1000) -> Dict:
        """Test backpressure with slow message consumption"""
        client = WebSocketTestClient("slow-consumer")
        # Use longer timeout as server might be busy from previous tests
        await client.connect(self.base_url, timeout=60.0)
        
        # Send many messages rapidly
        start = time.time()
        for i in range(message_count):
            await client.send({
                "type": "echo",
                "content": f"rapid-{i}"
            })
            
        send_duration = time.time() - start
        
        # Slowly consume
        await asyncio.sleep(2)
        received = len(client._received_messages)
        
        await client.close()
        
        return {
            "test": "slow_consumer",
            "sent": message_count,
            "received": received,
            "send_duration_ms": send_duration * 1000,
            "passed": received > message_count * 0.9  # 90% delivery
        }
        
    async def test_memory_stability(self, duration: int = 30,
                                     client_count: int = 50) -> Dict:
        """Test for memory leaks over time"""
        import psutil
        process = psutil.Process()
        
        initial_memory = process.memory_info().rss / 1024 / 1024
        memory_samples = [initial_memory]
        
        clients = [WebSocketTestClient(f"mem-{i}") 
                  for i in range(client_count)]
        
        # Connect
        await asyncio.gather(*[c.connect(self.base_url) for c in clients])
        
        # Run workload and sample memory
        start = time.time()
        while time.time() - start < duration:
            # Send some messages
            for client in clients:
                await client.ping()
            await asyncio.sleep(1)
            memory_samples.append(process.memory_info().rss / 1024 / 1024)
            
        # Cleanup
        await asyncio.gather(*[c.close() for c in clients])
        
        final_memory = memory_samples[-1]
        memory_growth = final_memory - initial_memory
        max_memory = max(memory_samples)
        
        return {
            "test": "memory_stability",
            "duration_seconds": duration,
            "initial_memory_mb": initial_memory,
            "final_memory_mb": final_memory,
            "max_memory_mb": max_memory,
            "memory_growth_mb": memory_growth,
            "passed": memory_growth < 50  # Less than 50MB growth
        }
        
    async def run_all_tests(self) -> List[Dict]:
        """Run all chaos tests"""
        results = []
        
        print("Running chaos tests...")
        
        print("  - Connection recovery test")
        results.append(await self.test_connection_recovery())
        await asyncio.sleep(1)  # Brief pause between tests
        
        print("  - Message under load test")
        results.append(await self.test_message_under_load())
        await asyncio.sleep(1)  # Brief pause between tests
        
        print("  - Slow consumer test")
        results.append(await self.test_slow_consumer())
        await asyncio.sleep(1)  # Brief pause between tests
        
        print("  - Memory stability test")
        results.append(await self.test_memory_stability())
        
        return results
