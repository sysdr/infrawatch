"""
Day 47: Notification Testing & Reliability System
Main application entry point with comprehensive testing capabilities
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from core.notification_service import NotificationService
from core.reliability_monitor import ReliabilityMonitor
from testing.test_orchestrator import TestOrchestrator
from testing.performance_tester import PerformanceTester
from monitoring.metrics_collector import MetricsCollector
from mocks.delivery_mocks import DeliveryMockManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global services
notification_service = NotificationService()
reliability_monitor = ReliabilityMonitor()
test_orchestrator = TestOrchestrator()
performance_tester = PerformanceTester()
metrics_collector = MetricsCollector()
mock_manager = DeliveryMockManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("🚀 Starting Notification Testing System...")
    await notification_service.initialize()
    await reliability_monitor.start()
    await metrics_collector.start()
    await mock_manager.initialize()
    
    # Start background monitoring task
    asyncio.create_task(background_monitoring())
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Notification Testing System...")
    await reliability_monitor.stop()
    await metrics_collector.stop()

app = FastAPI(
    title="Notification Testing & Reliability System",
    description="Comprehensive notification testing with reliability monitoring",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup static files path
import os
static_path = os.path.join(os.path.dirname(__file__), "..", "static")
if not os.path.exists(static_path):
    static_path = os.path.join(os.path.dirname(__file__), "static")

# WebSocket connections for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast_metrics(self, data: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except:
                self.disconnect(connection)

connection_manager = ConnectionManager()

async def background_monitoring():
    """Background task to collect and broadcast metrics"""
    while True:
        try:
            metrics = await metrics_collector.get_current_metrics()
            await connection_manager.broadcast_metrics(metrics)
            await asyncio.sleep(1)  # Update every second
        except Exception as e:
            logger.error(f"Error in background monitoring: {e}")
            await asyncio.sleep(5)

@app.websocket("/ws/metrics")
async def websocket_endpoint(websocket: WebSocket):
    await connection_manager.connect(websocket)
    try:
        # Send initial metrics
        metrics = await metrics_collector.get_current_metrics()
        await websocket.send_json(metrics)
        
        # Keep connection alive and receive messages
        while True:
            try:
                # Receive ping/pong messages to keep connection alive
                message = await websocket.receive_text()
                # Echo back or process if needed
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break
    except WebSocketDisconnect:
        pass
    finally:
        connection_manager.disconnect(websocket)

@app.get("/api/health")
async def health_check():
    """System health check endpoint"""
    health_status = await reliability_monitor.get_system_health()
    return {
        "status": "healthy" if health_status["overall_health"] > 0.8 else "degraded",
        "details": health_status,
        "timestamp": metrics_collector.get_timestamp()
    }

@app.post("/api/notifications/test")
async def test_notification(notification_data: dict):
    """Send a test notification"""
    try:
        result = await notification_service.send_notification(notification_data)
        channel = notification_data.get("channel", "unknown")
        
        # Record in metrics collector
        await metrics_collector.record_notification_attempt(
            channel,
            result["success"]
        )
        
        # Record in reliability monitor
        latency_ms = result.get("latency_ms", 0)
        reliability_monitor.record_delivery_attempt(
            channel,
            result["success"],
            latency_ms
        )
        
        return result
    except Exception as e:
        logger.error(f"Test notification failed: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/testing/integration")
async def run_integration_tests():
    """Run comprehensive integration tests"""
    try:
        results = await test_orchestrator.run_integration_tests()
        return {"success": True, "results": results}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/testing/performance")
async def run_performance_tests(test_config: dict):
    """Run performance tests with specified configuration"""
    try:
        results = await performance_tester.run_performance_test(test_config)
        return {"success": True, "results": results}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/metrics/current")
async def get_current_metrics():
    """Get current system metrics"""
    return await metrics_collector.get_current_metrics()

@app.get("/api/metrics/history")
async def get_metrics_history(hours: int = 1):
    """Get historical metrics"""
    return await metrics_collector.get_historical_metrics(hours)

@app.post("/api/mocks/configure")
async def configure_mocks(mock_config: dict):
    """Configure mock delivery services"""
    try:
        await mock_manager.configure_mocks(mock_config)
        return {"success": True, "message": "Mock services configured"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/circuit-breakers")
async def get_circuit_breaker_status():
    """Get circuit breaker status for all channels"""
    status = {}
    
    # Get actual circuit breaker states from NotificationService
    for channel in ["email", "sms", "push", "webhook"]:
        circuit_breaker = notification_service.circuit_breakers.get(channel)
        
        if circuit_breaker:
            cb_info = circuit_breaker.get_state_info()
            
            # Get metrics from reliability monitor
            recent_errors = reliability_monitor.error_counts.get(channel, 0)
            recent_total = reliability_monitor.total_counts.get(channel, 0)
            error_rate = recent_errors / max(recent_total, 1) if recent_total > 0 else 0.0
            
            status[channel] = {
                "state": cb_info["state"],  # "closed", "open", or "half_open"
                "error_rate": error_rate,
                "recent_errors": recent_errors,
                "recent_total": recent_total,
                "failure_count": cb_info["failure_count"],
                "failure_threshold": cb_info["failure_threshold"],
                "last_failure_time": cb_info["last_failure_time"]
            }
        else:
            # Fallback if circuit breaker not initialized
            recent_errors = reliability_monitor.error_counts.get(channel, 0)
            recent_total = reliability_monitor.total_counts.get(channel, 0)
            error_rate = recent_errors / max(recent_total, 1) if recent_total > 0 else 0.0
            
            status[channel] = {
                "state": "closed",
                "error_rate": error_rate,
                "recent_errors": recent_errors,
                "recent_total": recent_total,
                "failure_count": 0,
                "failure_threshold": 5,
                "last_failure_time": None
            }
    
    return status

# Serve static files
if os.path.exists(static_path):
    # Mount static assets directory (JS, CSS, etc.)
    static_assets_path = os.path.join(static_path, "static")
    if os.path.exists(static_assets_path):
        app.mount("/static", StaticFiles(directory=static_assets_path), name="static_files")
    
    # Serve index.html for root
    @app.get("/")
    async def read_root():
        index_path = os.path.join(static_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "Frontend not found. Please build the frontend."}
    
    # Catch-all route for SPA - serve index.html for all non-API routes
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Skip API and WebSocket routes (these should have been handled by earlier routes)
        if full_path.startswith("api/") or full_path.startswith("ws/"):
            return {"detail": "Not Found"}
        
        # Skip static files (these are handled by the mount)
        if full_path.startswith("static/"):
            return {"detail": "Not Found"}
        
        # For all other routes, serve index.html (SPA routing)
        index_path = os.path.join(static_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "Frontend not found. Please build the frontend."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
