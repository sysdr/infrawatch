from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import json
import time
import psutil
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict
import statistics
from app.testing.load_orchestrator import LoadTestOrchestrator, mixed_scenario

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
        # Optimize: only keep last 10000 latencies to avoid memory issues
        if len(self.latencies) > 10000:
            self.latencies = self.latencies[-10000:]
        
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
test_orchestrator: Optional[LoadTestOrchestrator] = None

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
    # If a test is running, use test orchestrator metrics
    if test_orchestrator and test_orchestrator.running:
        test_metrics = test_orchestrator.collect_metrics()
        connected_count = len([c for c in test_orchestrator.clients if c.connected])
        
        # Calculate latencies
        p50_latency = 0
        p95_latency = 0
        p99_latency = 0
        avg_latency = 0
        if test_metrics.all_latencies:
            sorted_lat = sorted(test_metrics.all_latencies)
            n = len(sorted_lat)
            p50_latency = sorted_lat[int(n * 0.5)] if n > 0 else 0
            p95_latency = sorted_lat[int(n * 0.95)] if n > 0 else 0
            p99_latency = sorted_lat[int(n * 0.99)] if n > 0 else 0
            avg_latency = statistics.mean(test_metrics.all_latencies)
        
        # Calculate throughput based on elapsed time (use start_time for real-time)
        elapsed = time.time() - test_orchestrator.start_time if test_orchestrator.start_time > 0 else 1
        throughput = test_metrics.total_messages_sent / max(1, elapsed)
        
        metrics = {
            "connections": connected_count,
            "total_messages": test_metrics.total_messages_sent,
            "errors": len(test_metrics.all_errors),
            "p50_latency": p50_latency,
            "p95_latency": p95_latency,
            "p99_latency": p99_latency,
            "avg_latency": avg_latency,
            "throughput": throughput,
            "uptime": time.time() - manager.start_time
        }
    else:
        # Use ConnectionManager metrics when no test is running
        metrics = manager.get_metrics()
    
    # Add system metrics (use cached values for performance)
    try:
        process = psutil.Process()
        metrics["cpu_percent"] = psutil.cpu_percent(interval=0.1)
        metrics["memory_mb"] = process.memory_info().rss / 1024 / 1024
        metrics["memory_percent"] = process.memory_percent()
    except Exception:
        metrics["cpu_percent"] = 0
        metrics["memory_mb"] = 0
        metrics["memory_percent"] = 0
    
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

async def run_load_test(test_config: Dict):
    """Background task to run the actual load test"""
    global current_test, test_orchestrator
    
    try:
        connections = test_config.get("connections", 50)
        duration = test_config.get("duration", 30)
        ramp_rate = min(200, max(50, connections // 2))  # Adaptive ramp rate
        
        # Create orchestrator
        test_orchestrator = LoadTestOrchestrator("ws://localhost:8000/ws")
        test_orchestrator.start_time = time.time()  # Set start time early for metrics
        
        # Update test status
        current_test["status"] = "running"
        current_test["progress"] = "Connecting..."
        
        # Spawn connections
        await test_orchestrator.spawn_connections(connections, ramp_rate)
        current_test["progress"] = f"Running test with {len(test_orchestrator.clients)} connections..."
        
        # Run scenario
        await test_orchestrator.execute_scenario(mixed_scenario, duration)
        
        # Collect metrics
        test_metrics = test_orchestrator.collect_metrics()
        
        # Update current test with results
        current_test["end_time"] = datetime.now().isoformat()
        current_test["status"] = "completed"
        current_test["progress"] = "Completed"
        current_test["results"] = {
            "connections": test_metrics.successful_connections,
            "p99_latency": test_metrics.p99_latency,
            "throughput": test_metrics.throughput_mps,
            "errors": len(test_metrics.all_errors),
            "p50_latency": test_metrics.p50_latency,
            "p95_latency": test_metrics.p95_latency
        }
        
        # Save to test results
        test_results.append(current_test.copy())
        
        # Cleanup
        await test_orchestrator.cleanup()
        test_orchestrator = None
        
    except Exception as e:
        current_test["status"] = "error"
        current_test["error"] = str(e)
        if test_orchestrator:
            await test_orchestrator.cleanup()
            test_orchestrator = None

@app.post("/api/tests/start")
async def start_test(test_config: Dict, background_tasks: BackgroundTasks):
    global current_test, test_orchestrator
    
    # Stop any running test first
    if test_orchestrator:
        await test_orchestrator.cleanup()
        test_orchestrator = None
    
    current_test = {
        "id": f"test-{int(time.time())}",
        "name": test_config.get("name", "unnamed"),
        "config": test_config,
        "start_time": datetime.now().isoformat(),
        "status": "starting",
        "progress": "Initializing..."
    }
    manager.reset_metrics()
    
    # Start background task
    background_tasks.add_task(run_load_test, test_config)
    
    return current_test

@app.post("/api/tests/stop")
async def stop_test():
    global current_test, test_orchestrator
    
    if test_orchestrator:
        await test_orchestrator.cleanup()
        test_orchestrator = None
    
    if current_test:
        current_test["end_time"] = datetime.now().isoformat()
        current_test["status"] = "stopped"
        if "results" not in current_test:
            current_test["results"] = manager.get_metrics()
        test_results.append(current_test.copy())
        result = current_test.copy()
        current_test = {}
        return result
    return {"error": "No test running"}

@app.get("/api/tests/current")
async def get_current_test():
    if current_test:
        response = {
            **current_test,
            "metrics": manager.get_metrics()
        }
        # Add connection count from orchestrator if running
        if test_orchestrator:
            response["active_connections"] = len([c for c in test_orchestrator.clients if c.connected])
        return response
    return {"status": "idle"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
