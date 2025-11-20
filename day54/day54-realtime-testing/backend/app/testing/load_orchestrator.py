import asyncio
import time
from typing import List, Dict, Callable
from dataclasses import dataclass, field
import statistics
from .ws_client import WebSocketTestClient, ConnectionMetrics

@dataclass
class AggregatedMetrics:
    total_connections: int = 0
    successful_connections: int = 0
    failed_connections: int = 0
    total_messages_sent: int = 0
    total_messages_received: int = 0
    total_bytes_sent: int = 0
    total_bytes_received: int = 0
    all_latencies: List[float] = field(default_factory=list)
    all_errors: List[str] = field(default_factory=list)
    test_duration: float = 0
    
    @property
    def connection_success_rate(self) -> float:
        if self.total_connections == 0:
            return 0
        return self.successful_connections / self.total_connections
    
    @property
    def p50_latency(self) -> float:
        if not self.all_latencies:
            return 0
        sorted_lat = sorted(self.all_latencies)
        return sorted_lat[int(len(sorted_lat) * 0.5)]
    
    @property
    def p95_latency(self) -> float:
        if not self.all_latencies:
            return 0
        sorted_lat = sorted(self.all_latencies)
        return sorted_lat[int(len(sorted_lat) * 0.95)]
    
    @property
    def p99_latency(self) -> float:
        if not self.all_latencies:
            return 0
        sorted_lat = sorted(self.all_latencies)
        return sorted_lat[int(len(sorted_lat) * 0.99)]
    
    @property
    def throughput_mps(self) -> float:
        if self.test_duration == 0:
            return 0
        return self.total_messages_sent / self.test_duration
    
    @property
    def error_rate(self) -> float:
        total = self.total_messages_sent + self.total_connections
        if total == 0:
            return 0
        return len(self.all_errors) / total
    
    def to_dict(self) -> Dict:
        return {
            "total_connections": self.total_connections,
            "successful_connections": self.successful_connections,
            "failed_connections": self.failed_connections,
            "connection_success_rate": self.connection_success_rate,
            "total_messages_sent": self.total_messages_sent,
            "total_messages_received": self.total_messages_received,
            "throughput_mps": self.throughput_mps,
            "p50_latency_ms": self.p50_latency,
            "p95_latency_ms": self.p95_latency,
            "p99_latency_ms": self.p99_latency,
            "error_rate": self.error_rate,
            "total_errors": len(self.all_errors),
            "test_duration_s": self.test_duration
        }

class LoadTestOrchestrator:
    def __init__(self, base_url: str = "ws://localhost:8000/ws"):
        self.base_url = base_url
        self.clients: List[WebSocketTestClient] = []
        self.metrics = AggregatedMetrics()
        self.running = False
        self.start_time: float = 0
        
    async def spawn_connections(self, count: int, ramp_rate: int = 100):
        """Spawn connections with controlled ramp rate"""
        self.metrics.total_connections = count
        delay = 1.0 / ramp_rate if ramp_rate > 0 else 0
        
        for i in range(count):
            client = WebSocketTestClient(f"load-test-{i}")
            try:
                await client.connect(self.base_url)
                self.clients.append(client)
                self.metrics.successful_connections += 1
            except Exception as e:
                self.metrics.failed_connections += 1
                self.metrics.all_errors.append(f"Connection {i}: {str(e)}")
                
            if delay > 0:
                await asyncio.sleep(delay)
                
    async def execute_scenario(self, scenario: Callable, duration: float = 60):
        """Execute a test scenario for specified duration"""
        self.running = True
        self.start_time = time.time()
        
        tasks = []
        for client in self.clients:
            if client.connected:
                task = asyncio.create_task(
                    self._run_client_scenario(client, scenario, duration)
                )
                tasks.append(task)
                
        await asyncio.gather(*tasks, return_exceptions=True)
        self.metrics.test_duration = time.time() - self.start_time
        self.running = False
        
    async def _run_client_scenario(self, client: WebSocketTestClient, 
                                    scenario: Callable, duration: float):
        """Run scenario for a single client"""
        start = time.time()
        while time.time() - start < duration and client.connected:
            try:
                await scenario(client)
            except Exception as e:
                self.metrics.all_errors.append(f"{client.client_id}: {str(e)}")
                break
                
    def collect_metrics(self) -> AggregatedMetrics:
        """Aggregate metrics from all clients (fresh collection each time)"""
        # Reset aggregated metrics
        self.metrics.total_messages_sent = 0
        self.metrics.total_messages_received = 0
        self.metrics.total_bytes_sent = 0
        self.metrics.total_bytes_received = 0
        self.metrics.all_latencies = []
        self.metrics.all_errors = []
        
        # Collect fresh metrics from all clients
        for client in self.clients:
            if client.connected:
                client_metrics = client.get_metrics()
                self.metrics.total_messages_sent += client_metrics.messages_sent
                self.metrics.total_messages_received += client_metrics.messages_received
                self.metrics.total_bytes_sent += client_metrics.bytes_sent
                self.metrics.total_bytes_received += client_metrics.bytes_received
                self.metrics.all_latencies.extend(client_metrics.latencies)
                self.metrics.all_errors.extend(client_metrics.errors)
            
        return self.metrics
    
    async def cleanup(self):
        """Close all connections"""
        for client in self.clients:
            await client.close()
        self.clients = []
        
    async def generate_report(self) -> Dict:
        """Generate test report"""
        return {
            "summary": self.metrics.to_dict(),
            "passed": self._check_thresholds(),
            "timestamp": time.time()
        }
        
    def _check_thresholds(self, p99_threshold: float = 100, 
                          error_threshold: float = 0.01) -> bool:
        """Check if test passes thresholds"""
        return (
            self.metrics.p99_latency < p99_threshold and
            self.metrics.error_rate < error_threshold and
            self.metrics.connection_success_rate > 0.99
        )

# Standard test scenarios
async def ping_scenario(client: WebSocketTestClient):
    """Simple ping-pong scenario"""
    await client.ping()
    await asyncio.sleep(0.1)
    
async def message_flood_scenario(client: WebSocketTestClient):
    """High-throughput message scenario"""
    await client.send_message(f"Test message from {client.client_id}")
    await asyncio.sleep(0.01)
    
async def mixed_scenario(client: WebSocketTestClient):
    """Mixed workload scenario"""
    import random
    if random.random() < 0.3:
        await client.ping()
    else:
        await client.send_message(f"Message {time.time()}")
    await asyncio.sleep(0.05)
