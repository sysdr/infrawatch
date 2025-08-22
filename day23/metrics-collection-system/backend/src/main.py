import asyncio
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import structlog
from core.ingestion.realtime_ingester import RealtimeIngester
from core.processing.batch_processor import BatchProcessor
from core.communication.agent_protocol import AgentProtocol
from core.scheduling.collection_scheduler import CollectionScheduler
from validation.metric_validator import MetricValidator
from api.metrics_api import metrics_router

logger = structlog.get_logger()

app = FastAPI(title="Metrics Collection Engine", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize core components
ingester = RealtimeIngester()
processor = BatchProcessor()
protocol = AgentProtocol()
scheduler = CollectionScheduler()
validator = MetricValidator()

# Inject components into the API
from api.metrics_api import components
components.update({
    "ingester": ingester,
    "processor": processor,
    "protocol": protocol,
    "scheduler": scheduler,
    "validator": validator
})

app.include_router(metrics_router, prefix="/api/v1")

@app.websocket("/ws/agent/{agent_id}")
async def agent_websocket(websocket: WebSocket, agent_id: str):
    await websocket.accept()
    try:
        await protocol.handle_agent_connection(websocket, agent_id, ingester, validator)
    except WebSocketDisconnect:
        logger.info(f"Agent {agent_id} disconnected")
    except Exception as e:
        logger.error(f"Agent {agent_id} error: {e}")

@app.websocket("/ws/dashboard")
async def dashboard_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        await protocol.handle_dashboard_connection(websocket, ingester)
    except WebSocketDisconnect:
        logger.info("Dashboard disconnected")

@app.on_event("startup")
async def startup():
    await ingester.start()
    await processor.start()
    await scheduler.start()
    logger.info("Metrics Collection Engine started")

@app.on_event("shutdown")
async def shutdown():
    await ingester.stop()
    await processor.stop()
    await scheduler.stop()
    logger.info("Metrics Collection Engine stopped")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, loop="uvloop")
