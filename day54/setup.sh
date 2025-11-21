#!/bin/bash

# Day 54: Real-time Testing - Complete Implementation Script
# Creates WebSocket testing suite with load testing, performance benchmarking, and UI dashboard

set -e

PROJECT_DIR="day54-realtime-testing"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
TESTS_DIR="$PROJECT_DIR/tests"

echo "=========================================="
echo "Day 54: Real-time Testing Implementation"
echo "=========================================="

# Cleanup previous installation
if [ -d "$PROJECT_DIR" ]; then
    echo "Cleaning up previous installation..."
    rm -rf "$PROJECT_DIR"
fi

# Create project structure
echo "Creating project structure..."
mkdir -p "$BACKEND_DIR/app"
mkdir -p "$BACKEND_DIR/app/core"
mkdir -p "$BACKEND_DIR/app/testing"
mkdir -p "$BACKEND_DIR/app/models"
mkdir -p "$TESTS_DIR/unit"
mkdir -p "$TESTS_DIR/integration"
mkdir -p "$TESTS_DIR/load"
mkdir -p "$TESTS_DIR/chaos"
mkdir -p "$FRONTEND_DIR/src/components"
mkdir -p "$FRONTEND_DIR/public"
mkdir -p "$PROJECT_DIR/reports"
mkdir -p "$PROJECT_DIR/scenarios"

# Backend requirements
cat > "$BACKEND_DIR/requirements.txt" << 'EOF'
fastapi==0.115.6
uvicorn[standard]==0.34.0
websockets==14.1
python-multipart==0.0.19
pydantic==2.10.4
pydantic-settings==2.7.0
redis==5.2.1
asyncio==3.4.3
aiohttp==3.11.11
pytest==8.3.4
pytest-asyncio==0.25.2
pytest-cov==6.0.0
httpx==0.28.1
locust==2.32.4
numpy==2.2.1
psutil==6.1.1
PyYAML==6.0.2
jinja2==3.1.5
EOF

# Main FastAPI application
cat > "$BACKEND_DIR/app/main.py" << 'EOF'
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import json
import time
import psutil
from datetime import datetime
from typing import Dict, List
from collections import defaultdict
import statistics

app = FastAPI(title="WebSocket Testing Suite", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_times: Dict[str, float] = {}
        self.message_counts: Dict[str, int] = defaultdict(int)
        self.latencies: List[float] = []
        self.errors: List[Dict] = []
        self.start_time = time.time()
        
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.connection_times[client_id] = time.time()
        
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            if client_id in self.connection_times:
                del self.connection_times[client_id]
                
    async def send_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)
            self.message_counts[client_id] += 1
            
    async def broadcast(self, message: str):
        for client_id in list(self.active_connections.keys()):
            try:
                await self.send_message(message, client_id)
            except Exception as e:
                self.errors.append({
                    "client_id": client_id,
                    "error": str(e),
                    "time": time.time()
                })
                
    def record_latency(self, latency_ms: float):
        self.latencies.append(latency_ms)
        
    def get_metrics(self) -> Dict:
        if not self.latencies:
            return {
                "connections": len(self.active_connections),
                "total_messages": sum(self.message_counts.values()),
                "errors": len(self.errors),
                "p50_latency": 0,
                "p95_latency": 0,
                "p99_latency": 0,
                "uptime": time.time() - self.start_time
            }
            
        sorted_latencies = sorted(self.latencies)
        n = len(sorted_latencies)
        
        return {
            "connections": len(self.active_connections),
            "total_messages": sum(self.message_counts.values()),
            "errors": len(self.errors),
            "p50_latency": sorted_latencies[int(n * 0.5)] if n > 0 else 0,
            "p95_latency": sorted_latencies[int(n * 0.95)] if n > 0 else 0,
            "p99_latency": sorted_latencies[int(n * 0.99)] if n > 0 else 0,
            "avg_latency": statistics.mean(self.latencies) if self.latencies else 0,
            "throughput": sum(self.message_counts.values()) / max(1, time.time() - self.start_time),
            "uptime": time.time() - self.start_time
        }
        
    def reset_metrics(self):
        self.latencies = []
        self.errors = []
        self.message_counts = defaultdict(int)
        self.start_time = time.time()

manager = ConnectionManager()

# Test results storage
test_results: List[Dict] = []
current_test: Dict = {}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Echo with timestamp for latency measurement
            if message.get("type") == "ping":
                response = {
                    "type": "pong",
                    "client_time": message.get("timestamp"),
                    "server_time": time.time() * 1000
                }
                await websocket.send_text(json.dumps(response))
                
                # Calculate and record latency
                if "timestamp" in message:
                    latency = (time.time() * 1000) - message["timestamp"]
                    manager.record_latency(latency)
                    
            elif message.get("type") == "message":
                # Broadcast to all clients
                await manager.broadcast(json.dumps({
                    "type": "broadcast",
                    "from": client_id,
                    "content": message.get("content"),
                    "timestamp": time.time() * 1000
                }))
                
            elif message.get("type") == "echo":
                await websocket.send_text(json.dumps({
                    "type": "echo_response",
                    "content": message.get("content"),
                    "timestamp": time.time() * 1000
                }))
                
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        manager.errors.append({
            "client_id": client_id,
            "error": str(e),
            "time": time.time()
        })
        manager.disconnect(client_id)

@app.get("/api/metrics")
async def get_metrics():
    metrics = manager.get_metrics()
    
    # Add system metrics
    process = psutil.Process()
    metrics["cpu_percent"] = psutil.cpu_percent()
    metrics["memory_mb"] = process.memory_info().rss / 1024 / 1024
    metrics["memory_percent"] = process.memory_percent()
    
    return metrics

@app.post("/api/metrics/reset")
async def reset_metrics():
    manager.reset_metrics()
    return {"status": "reset"}

@app.get("/api/connections")
async def get_connections():
    return {
        "count": len(manager.active_connections),
        "clients": list(manager.active_connections.keys())
    }

@app.get("/api/tests")
async def get_test_results():
    return test_results

@app.post("/api/tests/start")
async def start_test(test_config: Dict):
    global current_test
    current_test = {
        "id": f"test-{int(time.time())}",
        "name": test_config.get("name", "unnamed"),
        "config": test_config,
        "start_time": datetime.now().isoformat(),
        "status": "running"
    }
    manager.reset_metrics()
    return current_test

@app.post("/api/tests/stop")
async def stop_test():
    global current_test
    if current_test:
        current_test["end_time"] = datetime.now().isoformat()
        current_test["status"] = "completed"
        current_test["results"] = manager.get_metrics()
        test_results.append(current_test.copy())
        result = current_test.copy()
        current_test = {}
        return result
    return {"error": "No test running"}

@app.get("/api/tests/current")
async def get_current_test():
    if current_test:
        return {
            **current_test,
            "metrics": manager.get_metrics()
        }
    return {"status": "idle"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

# WebSocket test client
cat > "$BACKEND_DIR/app/testing/ws_client.py" << 'EOF'
import asyncio
import websockets
import json
import time
from dataclasses import dataclass, field
from typing import List, Optional
import statistics

@dataclass
class ConnectionMetrics:
    connection_time_ms: float = 0
    messages_sent: int = 0
    messages_received: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    latencies: List[float] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    @property
    def avg_latency(self) -> float:
        return statistics.mean(self.latencies) if self.latencies else 0
    
    @property
    def p95_latency(self) -> float:
        if not self.latencies:
            return 0
        sorted_lat = sorted(self.latencies)
        idx = int(len(sorted_lat) * 0.95)
        return sorted_lat[idx]
    
    @property
    def p99_latency(self) -> float:
        if not self.latencies:
            return 0
        sorted_lat = sorted(self.latencies)
        idx = int(len(sorted_lat) * 0.99)
        return sorted_lat[idx]

class WebSocketTestClient:
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.metrics = ConnectionMetrics()
        self.connected = False
        self._receive_task = None
        self._received_messages: List[dict] = []
        
    async def connect(self, url: str, headers: dict = None):
        start_time = time.time()
        try:
            self.ws = await websockets.connect(
                f"{url}/{self.client_id}",
                extra_headers=headers or {}
            )
            self.metrics.connection_time_ms = (time.time() - start_time) * 1000
            self.connected = True
            self._receive_task = asyncio.create_task(self._receive_loop())
        except Exception as e:
            self.metrics.errors.append(str(e))
            raise
            
    async def _receive_loop(self):
        try:
            async for message in self.ws:
                self.metrics.messages_received += 1
                self.metrics.bytes_received += len(message)
                data = json.loads(message)
                self._received_messages.append(data)
                
                # Record latency for pong messages
                if data.get("type") == "pong" and "client_time" in data:
                    latency = time.time() * 1000 - data["client_time"]
                    self.metrics.latencies.append(latency)
        except websockets.exceptions.ConnectionClosed:
            self.connected = False
        except Exception as e:
            self.metrics.errors.append(str(e))
            self.connected = False
            
    async def send(self, message: dict):
        if not self.ws or not self.connected:
            raise RuntimeError("Not connected")
        data = json.dumps(message)
        await self.ws.send(data)
        self.metrics.messages_sent += 1
        self.metrics.bytes_sent += len(data)
        
    async def ping(self):
        await self.send({
            "type": "ping",
            "timestamp": time.time() * 1000
        })
        
    async def send_message(self, content: str):
        await self.send({
            "type": "message",
            "content": content
        })
        
    async def receive(self, timeout: float = 5.0) -> dict:
        start = time.time()
        while time.time() - start < timeout:
            if self._received_messages:
                return self._received_messages.pop(0)
            await asyncio.sleep(0.01)
        raise TimeoutError("No message received within timeout")
        
    async def close(self):
        if self._receive_task:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass
        if self.ws:
            await self.ws.close()
        self.connected = False
        
    def get_metrics(self) -> ConnectionMetrics:
        return self.metrics
EOF

# Load test orchestrator
cat > "$BACKEND_DIR/app/testing/load_orchestrator.py" << 'EOF'
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
        start_time = time.time()
        
        tasks = []
        for client in self.clients:
            if client.connected:
                task = asyncio.create_task(
                    self._run_client_scenario(client, scenario, duration)
                )
                tasks.append(task)
                
        await asyncio.gather(*tasks, return_exceptions=True)
        self.metrics.test_duration = time.time() - start_time
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
        """Aggregate metrics from all clients"""
        for client in self.clients:
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
EOF

# Concurrency test framework
cat > "$BACKEND_DIR/app/testing/concurrency_tests.py" << 'EOF'
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
EOF

# Performance benchmarker
cat > "$BACKEND_DIR/app/testing/benchmarker.py" << 'EOF'
import asyncio
import time
from dataclasses import dataclass
from typing import Dict, List
import psutil
import json
from .load_orchestrator import LoadTestOrchestrator, ping_scenario, mixed_scenario

@dataclass
class PerformanceReport:
    test_name: str
    connections: int
    duration_seconds: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    avg_latency_ms: float
    throughput_mps: float
    total_messages: int
    error_count: int
    error_rate: float
    connection_time_ms: float
    memory_usage_mb: float
    cpu_percent: float
    passed: bool
    
    def to_dict(self) -> Dict:
        return {
            "test_name": self.test_name,
            "connections": self.connections,
            "duration_seconds": self.duration_seconds,
            "latency": {
                "p50_ms": self.p50_latency_ms,
                "p95_ms": self.p95_latency_ms,
                "p99_ms": self.p99_latency_ms,
                "avg_ms": self.avg_latency_ms
            },
            "throughput_mps": self.throughput_mps,
            "total_messages": self.total_messages,
            "errors": {
                "count": self.error_count,
                "rate": self.error_rate
            },
            "resources": {
                "memory_mb": self.memory_usage_mb,
                "cpu_percent": self.cpu_percent
            },
            "passed": self.passed
        }

class PerformanceBenchmarker:
    def __init__(self, base_url: str = "ws://localhost:8000/ws"):
        self.base_url = base_url
        self.reports: List[PerformanceReport] = []
        
    async def run_benchmark(
        self,
        name: str,
        connections: int,
        duration: float,
        ramp_rate: int = 100,
        scenario_type: str = "mixed"
    ) -> PerformanceReport:
        """Run a single benchmark test"""
        orchestrator = LoadTestOrchestrator(self.base_url)
        
        # Select scenario
        scenario = mixed_scenario if scenario_type == "mixed" else ping_scenario
        
        # Record initial resources
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024
        
        # Spawn connections
        connect_start = time.time()
        await orchestrator.spawn_connections(connections, ramp_rate)
        connection_time = (time.time() - connect_start) * 1000
        
        # Run scenario
        await orchestrator.execute_scenario(scenario, duration)
        
        # Collect metrics
        metrics = orchestrator.collect_metrics()
        
        # Record final resources
        final_memory = process.memory_info().rss / 1024 / 1024
        cpu_percent = psutil.cpu_percent()
        
        # Cleanup
        await orchestrator.cleanup()
        
        # Create report
        report = PerformanceReport(
            test_name=name,
            connections=connections,
            duration_seconds=duration,
            p50_latency_ms=metrics.p50_latency,
            p95_latency_ms=metrics.p95_latency,
            p99_latency_ms=metrics.p99_latency,
            avg_latency_ms=sum(metrics.all_latencies) / len(metrics.all_latencies) if metrics.all_latencies else 0,
            throughput_mps=metrics.throughput_mps,
            total_messages=metrics.total_messages_sent,
            error_count=len(metrics.all_errors),
            error_rate=metrics.error_rate,
            connection_time_ms=connection_time,
            memory_usage_mb=final_memory - initial_memory,
            cpu_percent=cpu_percent,
            passed=metrics.p99_latency < 100 and metrics.error_rate < 0.01
        )
        
        self.reports.append(report)
        return report
        
    async def run_standard_benchmarks(self) -> List[PerformanceReport]:
        """Run standard benchmark suite"""
        benchmarks = [
            ("small_load", 50, 30),
            ("medium_load", 200, 30),
            ("large_load", 500, 30),
            ("stress_test", 1000, 60)
        ]
        
        results = []
        for name, connections, duration in benchmarks:
            print(f"Running benchmark: {name} ({connections} connections, {duration}s)")
            report = await self.run_benchmark(name, connections, duration)
            results.append(report)
            print(f"  P99 Latency: {report.p99_latency_ms:.2f}ms, "
                  f"Throughput: {report.throughput_mps:.0f} msg/s, "
                  f"Passed: {report.passed}")
            
        return results
        
    def export_results(self, filepath: str):
        """Export results to JSON file"""
        data = {
            "benchmark_results": [r.to_dict() for r in self.reports],
            "timestamp": time.time()
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
EOF

# Chaos test framework
cat > "$BACKEND_DIR/app/testing/chaos_tests.py" << 'EOF'
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
        await client.connect(self.base_url)
        
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
        
        print("  - Message under load test")
        results.append(await self.test_message_under_load())
        
        print("  - Slow consumer test")
        results.append(await self.test_slow_consumer())
        
        print("  - Memory stability test")
        results.append(await self.test_memory_stability())
        
        return results
EOF

# Unit tests
cat > "$TESTS_DIR/unit/test_ws_client.py" << 'EOF'
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
EOF

# Integration tests
cat > "$TESTS_DIR/integration/test_websocket_server.py" << 'EOF'
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
EOF

# Load test runner
cat > "$TESTS_DIR/load/test_load.py" << 'EOF'
import pytest
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))
from app.testing.load_orchestrator import (
    LoadTestOrchestrator, 
    ping_scenario, 
    mixed_scenario
)
from app.testing.benchmarker import PerformanceBenchmarker

BASE_URL = "ws://localhost:8000/ws"

class TestLoadScenarios:
    @pytest.mark.asyncio
    async def test_small_load(self):
        orchestrator = LoadTestOrchestrator(BASE_URL)
        
        # Spawn 50 connections
        await orchestrator.spawn_connections(50, ramp_rate=50)
        
        # Run for 10 seconds
        await orchestrator.execute_scenario(ping_scenario, 10)
        
        metrics = orchestrator.collect_metrics()
        await orchestrator.cleanup()
        
        assert metrics.successful_connections >= 45  # 90% success
        assert metrics.p99_latency < 500  # Under 500ms
        
    @pytest.mark.asyncio
    async def test_medium_load(self):
        orchestrator = LoadTestOrchestrator(BASE_URL)
        
        await orchestrator.spawn_connections(100, ramp_rate=50)
        await orchestrator.execute_scenario(mixed_scenario, 15)
        
        metrics = orchestrator.collect_metrics()
        await orchestrator.cleanup()
        
        assert metrics.connection_success_rate > 0.9
        assert metrics.throughput_mps > 0
        
    @pytest.mark.asyncio
    async def test_ramp_up(self):
        orchestrator = LoadTestOrchestrator(BASE_URL)
        
        # Slow ramp to test gradual load
        await orchestrator.spawn_connections(200, ramp_rate=20)
        await orchestrator.execute_scenario(ping_scenario, 20)
        
        metrics = orchestrator.collect_metrics()
        await orchestrator.cleanup()
        
        assert metrics.successful_connections >= 180

class TestBenchmarks:
    @pytest.mark.asyncio
    async def test_benchmark_suite(self):
        benchmarker = PerformanceBenchmarker(BASE_URL)
        
        # Run small benchmark
        report = await benchmarker.run_benchmark(
            "quick_test",
            connections=30,
            duration=10
        )
        
        assert report.total_messages > 0
        assert report.throughput_mps > 0
EOF

# Chaos test runner
cat > "$TESTS_DIR/chaos/test_chaos.py" << 'EOF'
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
EOF

# Test runner script
cat > "$BACKEND_DIR/run_tests.py" << 'EOF'
#!/usr/bin/env python3
"""
Complete test suite runner for WebSocket testing
"""
import asyncio
import sys
import json
import time
from datetime import datetime

sys.path.insert(0, '.')
from app.testing.load_orchestrator import LoadTestOrchestrator, mixed_scenario
from app.testing.benchmarker import PerformanceBenchmarker
from app.testing.concurrency_tests import ConcurrencyTestSuite
from app.testing.chaos_tests import ChaosTestSuite

BASE_URL = "ws://localhost:8000/ws"

async def run_full_test_suite():
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": []
    }
    
    print("=" * 60)
    print("WebSocket Testing Suite - Full Run")
    print("=" * 60)
    
    # Concurrency Tests
    print("\n[1/3] Running Concurrency Tests...")
    concurrency_suite = ConcurrencyTestSuite(BASE_URL)
    concurrency_results = await concurrency_suite.run_all_tests()
    
    for result in concurrency_results:
        status = "✓ PASS" if result["passed"] else "✗ FAIL"
        print(f"  {status} - {result['test']}")
        results["tests"].append(result)
        
    # Chaos Tests
    print("\n[2/3] Running Chaos Tests...")
    chaos_suite = ChaosTestSuite(BASE_URL)
    chaos_results = await chaos_suite.run_all_tests()
    
    for result in chaos_results:
        status = "✓ PASS" if result["passed"] else "✗ FAIL"
        print(f"  {status} - {result['test']}")
        results["tests"].append(result)
        
    # Performance Benchmarks
    print("\n[3/3] Running Performance Benchmarks...")
    benchmarker = PerformanceBenchmarker(BASE_URL)
    
    # Quick benchmark for demo
    report = await benchmarker.run_benchmark(
        "demo_benchmark",
        connections=100,
        duration=15
    )
    
    benchmark_result = {
        "test": "performance_benchmark",
        "passed": report.passed,
        "p99_latency_ms": report.p99_latency_ms,
        "throughput_mps": report.throughput_mps,
        "error_rate": report.error_rate
    }
    results["tests"].append(benchmark_result)
    
    status = "✓ PASS" if report.passed else "✗ FAIL"
    print(f"  {status} - Performance Benchmark")
    print(f"    P99 Latency: {report.p99_latency_ms:.2f}ms")
    print(f"    Throughput: {report.throughput_mps:.0f} msg/s")
    
    # Summary
    print("\n" + "=" * 60)
    total = len(results["tests"])
    passed = sum(1 for t in results["tests"] if t["passed"])
    failed = total - passed
    
    print(f"Results: {passed}/{total} tests passed")
    if failed > 0:
        print(f"  ✗ {failed} tests failed")
    else:
        print("  ✓ All tests passed!")
        
    # Save results
    with open("reports/test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to reports/test_results.json")
    
    return failed == 0

if __name__ == "__main__":
    success = asyncio.run(run_full_test_suite())
    sys.exit(0 if success else 1)
EOF

# Frontend React application
cat > "$FRONTEND_DIR/package.json" << 'EOF'
{
  "name": "websocket-testing-dashboard",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-scripts": "5.0.1",
    "recharts": "^2.15.0",
    "axios": "^1.7.9"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build"
  },
  "browserslist": {
    "production": [">0.2%", "not dead", "not op_mini all"],
    "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
  }
}
EOF

# Frontend index.html
cat > "$FRONTEND_DIR/public/index.html" << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>WebSocket Testing Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div id="root"></div>
</body>
</html>
EOF

# Main React App
cat > "$FRONTEND_DIR/src/index.js" << 'EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
EOF

# Main App component
cat > "$FRONTEND_DIR/src/App.js" << 'EOF'
import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, PieChart, Pie, Cell
} from 'recharts';

const API_BASE = 'http://localhost:8000/api';

function App() {
  const [metrics, setMetrics] = useState({
    connections: 0,
    total_messages: 0,
    errors: 0,
    p50_latency: 0,
    p95_latency: 0,
    p99_latency: 0,
    throughput: 0,
    cpu_percent: 0,
    memory_mb: 0
  });
  const [metricsHistory, setMetricsHistory] = useState([]);
  const [testResults, setTestResults] = useState([]);
  const [currentTest, setCurrentTest] = useState(null);
  const [isRunning, setIsRunning] = useState(false);

  const fetchMetrics = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE}/metrics`);
      const newMetrics = response.data;
      setMetrics(newMetrics);
      
      setMetricsHistory(prev => {
        const updated = [...prev, {
          time: new Date().toLocaleTimeString(),
          connections: newMetrics.connections,
          latency: newMetrics.p99_latency,
          throughput: newMetrics.throughput,
          errors: newMetrics.errors
        }];
        return updated.slice(-30);
      });
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    }
  }, []);

  const fetchTestResults = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE}/tests`);
      setTestResults(response.data);
    } catch (error) {
      console.error('Failed to fetch test results:', error);
    }
  }, []);

  const fetchCurrentTest = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE}/tests/current`);
      setCurrentTest(response.data);
      setIsRunning(response.data.status === 'running');
    } catch (error) {
      console.error('Failed to fetch current test:', error);
    }
  }, []);

  useEffect(() => {
    fetchMetrics();
    fetchTestResults();
    fetchCurrentTest();
    
    const interval = setInterval(() => {
      fetchMetrics();
      fetchCurrentTest();
    }, 1000);
    
    return () => clearInterval(interval);
  }, [fetchMetrics, fetchTestResults, fetchCurrentTest]);

  const startTest = async (testConfig) => {
    try {
      await axios.post(`${API_BASE}/tests/start`, testConfig);
      setIsRunning(true);
    } catch (error) {
      console.error('Failed to start test:', error);
    }
  };

  const stopTest = async () => {
    try {
      await axios.post(`${API_BASE}/tests/stop`);
      setIsRunning(false);
      fetchTestResults();
    } catch (error) {
      console.error('Failed to stop test:', error);
    }
  };

  const resetMetrics = async () => {
    try {
      await axios.post(`${API_BASE}/metrics/reset`);
      setMetricsHistory([]);
    } catch (error) {
      console.error('Failed to reset metrics:', error);
    }
  };

  const latencyData = [
    { name: 'P50', value: metrics.p50_latency, fill: '#10B981' },
    { name: 'P95', value: metrics.p95_latency, fill: '#F59E0B' },
    { name: 'P99', value: metrics.p99_latency, fill: '#EF4444' }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                WebSocket Testing Dashboard
              </h1>
              <p className="text-sm text-gray-500">Real-time performance monitoring</p>
            </div>
            <div className="flex items-center gap-3">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                isRunning 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-gray-100 text-gray-800'
              }`}>
                {isRunning ? '● Running' : '○ Idle'}
              </span>
              <button
                onClick={resetMetrics}
                className="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition"
              >
                Reset
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        {/* Metrics Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <MetricCard 
            title="Connections" 
            value={metrics.connections} 
            color="blue"
          />
          <MetricCard 
            title="Messages" 
            value={metrics.total_messages} 
            color="green"
          />
          <MetricCard 
            title="Throughput" 
            value={`${metrics.throughput?.toFixed(0) || 0}/s`} 
            color="purple"
          />
          <MetricCard 
            title="Errors" 
            value={metrics.errors} 
            color={metrics.errors > 0 ? "red" : "gray"}
          />
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Latency Distribution */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h3 className="text-lg font-semibold mb-4">Latency Distribution (ms)</h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={latencyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                  {latencyData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Throughput Timeline */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h3 className="text-lg font-semibold mb-4">Throughput Timeline</h3>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={metricsHistory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="throughput" 
                  stroke="#8B5CF6" 
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* System Resources */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h3 className="text-lg font-semibold mb-4">CPU Usage</h3>
            <div className="flex items-center justify-center">
              <div className="relative w-32 h-32">
                <svg className="w-full h-full transform -rotate-90">
                  <circle
                    cx="64"
                    cy="64"
                    r="56"
                    stroke="#E5E7EB"
                    strokeWidth="8"
                    fill="none"
                  />
                  <circle
                    cx="64"
                    cy="64"
                    r="56"
                    stroke="#3B82F6"
                    strokeWidth="8"
                    fill="none"
                    strokeDasharray={`${(metrics.cpu_percent / 100) * 351.86} 351.86`}
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-2xl font-bold">{metrics.cpu_percent?.toFixed(0)}%</span>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <h3 className="text-lg font-semibold mb-4">Memory Usage</h3>
            <div className="text-center">
              <span className="text-4xl font-bold text-purple-600">
                {metrics.memory_mb?.toFixed(0)}
              </span>
              <span className="text-lg text-gray-500 ml-1">MB</span>
            </div>
            <div className="mt-4 h-3 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className="h-full bg-purple-500 transition-all duration-500"
                style={{ width: `${Math.min(metrics.memory_percent || 0, 100)}%` }}
              />
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <h3 className="text-lg font-semibold mb-4">Connection Timeline</h3>
            <ResponsiveContainer width="100%" height={100}>
              <LineChart data={metricsHistory}>
                <Line 
                  type="monotone" 
                  dataKey="connections" 
                  stroke="#10B981" 
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Test Controls */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">Test Controls</h3>
          <div className="flex flex-wrap gap-3">
            <button
              onClick={() => startTest({ name: 'quick_test', connections: 50, duration: 30 })}
              disabled={isRunning}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
            >
              Quick Test (50 conn)
            </button>
            <button
              onClick={() => startTest({ name: 'load_test', connections: 200, duration: 60 })}
              disabled={isRunning}
              className="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
            >
              Load Test (200 conn)
            </button>
            <button
              onClick={() => startTest({ name: 'stress_test', connections: 500, duration: 60 })}
              disabled={isRunning}
              className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
            >
              Stress Test (500 conn)
            </button>
            <button
              onClick={stopTest}
              disabled={!isRunning}
              className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
            >
              Stop Test
            </button>
          </div>
        </div>

        {/* Test Results */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold mb-4">Test History</h3>
          {testResults.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No test results yet</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4 font-medium text-gray-600">Test</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-600">Status</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-600">P99 Latency</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-600">Throughput</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-600">Time</th>
                  </tr>
                </thead>
                <tbody>
                  {testResults.slice().reverse().map((test, index) => (
                    <tr key={index} className="border-b hover:bg-gray-50">
                      <td className="py-3 px-4 font-medium">{test.name}</td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          test.status === 'completed' 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {test.status}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        {test.results?.p99_latency?.toFixed(2) || '-'} ms
                      </td>
                      <td className="py-3 px-4">
                        {test.results?.throughput?.toFixed(0) || '-'} msg/s
                      </td>
                      <td className="py-3 px-4 text-gray-500 text-sm">
                        {new Date(test.start_time).toLocaleTimeString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

function MetricCard({ title, value, color }) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-700 border-blue-200',
    green: 'bg-green-50 text-green-700 border-green-200',
    purple: 'bg-purple-50 text-purple-700 border-purple-200',
    red: 'bg-red-50 text-red-700 border-red-200',
    gray: 'bg-gray-50 text-gray-700 border-gray-200'
  };

  return (
    <div className={`rounded-xl border p-4 ${colorClasses[color]}`}>
      <p className="text-sm font-medium opacity-75">{title}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
    </div>
  );
}

export default App;
EOF

# Scenario configuration
cat > "$PROJECT_DIR/scenarios/load_test.yaml" << 'EOF'
name: standard_load_test
description: Standard load testing scenario

phases:
  - name: ramp_up
    duration: 60
    target_connections: 500
    message_rate: 10
    
  - name: steady_state
    duration: 120
    target_connections: 500
    message_rate: 10
    
  - name: spike
    duration: 30
    target_connections: 1000
    message_rate: 20
    
  - name: recovery
    duration: 60
    target_connections: 500
    message_rate: 10

thresholds:
  p99_latency_ms: 100
  error_rate: 0.01
  connection_success_rate: 0.99
  min_throughput_mps: 1000
EOF

# Docker configuration
cat > "$PROJECT_DIR/Dockerfile" << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

cat > "$PROJECT_DIR/docker-compose.yml" << 'EOF'
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 3

  frontend:
    image: node:20-alpine
    working_dir: /app
    volumes:
      - ./frontend:/app
    ports:
      - "3000:3000"
    command: sh -c "npm install && npm start"
    environment:
      - CHOKIDAR_USEPOLLING=true
    depends_on:
      - backend
EOF

# Build script
cat > "$PROJECT_DIR/build.sh" << 'EOF'
#!/bin/bash
set -e

echo "=========================================="
echo "Day 54: Real-time Testing - Build & Run"
echo "=========================================="

cd "$(dirname "$0")"

# Check for Docker mode
USE_DOCKER=false
if [ "$1" = "--docker" ]; then
    USE_DOCKER=true
fi

if [ "$USE_DOCKER" = true ]; then
    echo ""
    echo "[Docker Mode]"
    echo "Building and starting services..."
    
    docker-compose up --build -d
    
    echo "Waiting for services to start..."
    sleep 10
    
    echo ""
    echo "Services running:"
    echo "  - Backend: http://localhost:8000"
    echo "  - Frontend: http://localhost:3000"
    echo ""
    echo "Health check:"
    curl -s http://localhost:8000/health | python3 -m json.tool
    
else
    echo ""
    echo "[Local Mode]"
    
    # Create virtual environment
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    
    # Install backend dependencies
    echo "Installing backend dependencies..."
    pip install -r backend/requirements.txt
    
    # Start backend server
    echo "Starting backend server..."
    cd backend
    uvicorn app.main:app --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ..
    
    # Wait for backend
    echo "Waiting for backend to start..."
    sleep 5
    
    # Health check
    echo "Backend health check:"
    curl -s http://localhost:8000/health | python3 -m json.tool
    
    # Install and start frontend
    echo ""
    echo "Installing frontend dependencies..."
    cd frontend
    npm install
    
    echo "Starting frontend..."
    PORT=3000 npm start &
    FRONTEND_PID=$!
    cd ..
    
    # Save PIDs
    echo $BACKEND_PID > .backend.pid
    echo $FRONTEND_PID > .frontend.pid
    
    echo ""
    echo "Services running:"
    echo "  - Backend: http://localhost:8000 (PID: $BACKEND_PID)"
    echo "  - Frontend: http://localhost:3000 (PID: $FRONTEND_PID)"
fi

echo ""
echo "=========================================="
echo "Running Unit Tests"
echo "=========================================="

if [ "$USE_DOCKER" = true ]; then
    docker-compose exec -T backend pytest tests/unit -v
else
    source venv/bin/activate
    cd backend
    python -m pytest ../tests/unit -v
    cd ..
fi

echo ""
echo "=========================================="
echo "Running Integration Tests"
echo "=========================================="

if [ "$USE_DOCKER" = true ]; then
    docker-compose exec -T backend pytest tests/integration -v
else
    source venv/bin/activate
    cd backend
    python -m pytest ../tests/integration -v
    cd ..
fi

echo ""
echo "=========================================="
echo "Running Load Tests"
echo "=========================================="

if [ "$USE_DOCKER" = true ]; then
    docker-compose exec -T backend pytest tests/load -v --timeout=120
else
    source venv/bin/activate
    cd backend
    python -m pytest ../tests/load -v --timeout=120
    cd ..
fi

echo ""
echo "=========================================="
echo "Running Chaos Tests"
echo "=========================================="

if [ "$USE_DOCKER" = true ]; then
    docker-compose exec -T backend pytest tests/chaos -v --timeout=120
else
    source venv/bin/activate
    cd backend
    python -m pytest ../tests/chaos -v --timeout=120
    cd ..
fi

echo ""
echo "=========================================="
echo "Running Full Test Suite"
echo "=========================================="

if [ "$USE_DOCKER" = true ]; then
    docker-compose exec -T backend python run_tests.py
else
    source venv/bin/activate
    cd backend
    python run_tests.py
    cd ..
fi

echo ""
echo "=========================================="
echo "Build Complete!"
echo "=========================================="
echo ""
echo "Dashboard: http://localhost:3000"
echo "API Docs:  http://localhost:8000/docs"
echo "Metrics:   http://localhost:8000/api/metrics"
echo ""
echo "Test results saved to: reports/test_results.json"
EOF

# Stop script
cat > "$PROJECT_DIR/stop.sh" << 'EOF'
#!/bin/bash

echo "Stopping services..."

cd "$(dirname "$0")"

# Stop Docker services if running
if docker-compose ps -q 2>/dev/null; then
    echo "Stopping Docker services..."
    docker-compose down
fi

# Stop local processes
if [ -f .backend.pid ]; then
    BACKEND_PID=$(cat .backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
    fi
    rm .backend.pid
fi

if [ -f .frontend.pid ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
    fi
    rm .frontend.pid
fi

# Kill any remaining processes on ports
for port in 8000 3000; do
    pid=$(lsof -t -i:$port 2>/dev/null)
    if [ -n "$pid" ]; then
        echo "Killing process on port $port (PID: $pid)"
        kill $pid 2>/dev/null
    fi
done

echo "All services stopped."
EOF

# Make scripts executable
chmod +x "$PROJECT_DIR/build.sh"
chmod +x "$PROJECT_DIR/stop.sh"
chmod +x "$BACKEND_DIR/run_tests.py"

# Pytest configuration
cat > "$PROJECT_DIR/pytest.ini" << 'EOF'
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_functions = test_*
addopts = -v --tb=short
EOF

echo ""
echo "=========================================="
echo "Project Structure Created Successfully!"
echo "=========================================="
echo ""
echo "To build and run:"
echo "  cd $PROJECT_DIR"
echo "  ./build.sh          # Local mode"
echo "  ./build.sh --docker # Docker mode"
echo ""
echo "To stop:"
echo "  ./stop.sh"
echo ""

# Verify file structure
echo "Verifying file structure..."
echo ""

files=(
    "$BACKEND_DIR/app/main.py"
    "$BACKEND_DIR/app/testing/ws_client.py"
    "$BACKEND_DIR/app/testing/load_orchestrator.py"
    "$BACKEND_DIR/app/testing/concurrency_tests.py"
    "$BACKEND_DIR/app/testing/chaos_tests.py"
    "$BACKEND_DIR/app/testing/benchmarker.py"
    "$BACKEND_DIR/requirements.txt"
    "$BACKEND_DIR/run_tests.py"
    "$TESTS_DIR/unit/test_ws_client.py"
    "$TESTS_DIR/integration/test_websocket_server.py"
    "$TESTS_DIR/load/test_load.py"
    "$TESTS_DIR/chaos/test_chaos.py"
    "$FRONTEND_DIR/package.json"
    "$FRONTEND_DIR/src/App.js"
    "$FRONTEND_DIR/src/index.js"
    "$FRONTEND_DIR/public/index.html"
    "$PROJECT_DIR/docker-compose.yml"
    "$PROJECT_DIR/Dockerfile"
    "$PROJECT_DIR/build.sh"
    "$PROJECT_DIR/stop.sh"
)

all_present=true
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (MISSING)"
        all_present=false
    fi
done

echo ""
if [ "$all_present" = true ]; then
    echo "All files created successfully!"
else
    echo "WARNING: Some files are missing!"
fi

# Create __init__.py files
touch "$BACKEND_DIR/app/__init__.py"
touch "$BACKEND_DIR/app/core/__init__.py"
touch "$BACKEND_DIR/app/testing/__init__.py"
touch "$BACKEND_DIR/app/models/__init__.py"
touch "$TESTS_DIR/__init__.py"
touch "$TESTS_DIR/unit/__init__.py"
touch "$TESTS_DIR/integration/__init__.py"
touch "$TESTS_DIR/load/__init__.py"
touch "$TESTS_DIR/chaos/__init__.py"

echo ""
echo "Implementation script complete!"