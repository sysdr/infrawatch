import asyncio
import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import websockets

from app.services.state_manager import StateManager
from app.services.alert_evaluator import AlertEvaluator
from app.services.notification_router import NotificationRouter
from app.websocket.coordinator import WebSocketCoordinator
from app.websocket.handler import WebSocketHandler
from app.api.routes import create_routes
from app.models import AlertRule, AlertSeverity

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Alert System Integration", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
websocket_coordinator = WebSocketCoordinator()
state_manager = StateManager(websocket_coordinator)
notification_router = NotificationRouter(state_manager)
alert_evaluator = AlertEvaluator(state_manager, notification_router)
websocket_handler = WebSocketHandler(websocket_coordinator, state_manager)

# Create routes
create_routes(app, state_manager, alert_evaluator)

async def init_sample_rules():
    """Initialize sample alert rules"""
    sample_rules = [
        AlertRule(
            id="rule_cpu_high",
            name="High CPU Usage",
            metric="cpu_usage",
            condition=">",
            threshold=80.0,
            duration=30,
            severity=AlertSeverity.WARNING,
            labels={"service": "web", "env": "production"}
        ),
        AlertRule(
            id="rule_memory_critical",
            name="Critical Memory Usage",
            metric="memory_usage",
            condition=">",
            threshold=90.0,
            duration=10,
            severity=AlertSeverity.CRITICAL,
            labels={"service": "database", "env": "production"}
        ),
        AlertRule(
            id="rule_response_time",
            name="Slow Response Time",
            metric="response_time_ms",
            condition=">",
            threshold=1000.0,
            duration=60,
            severity=AlertSeverity.WARNING,
            labels={"service": "api", "env": "production"}
        )
    ]
    
    for rule in sample_rules:
        await state_manager.add_rule(rule)
    
    logger.info(f"Initialized {len(sample_rules)} sample alert rules")

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting Alert System Integration...")
    await init_sample_rules()
    logger.info("✅ Alert engine started")

async def start_websocket_server():
    """Start WebSocket server"""
    async with websockets.serve(
        websocket_handler.handle_connection,
        "0.0.0.0",
        8001
    ):
        logger.info("✅ WebSocket server listening on :8001")
        await asyncio.Future()  # Run forever

async def main():
    """Main entry point"""
    # Start WebSocket server in background
    websocket_task = asyncio.create_task(start_websocket_server())
    
    # Start FastAPI server
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000,
        loop="asyncio"
    )
    server = uvicorn.Server(config)
    
    # Run both servers concurrently
    await asyncio.gather(
        websocket_task,
        server.serve()
    )

if __name__ == "__main__":
    asyncio.run(main())
