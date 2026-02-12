from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from contextlib import asynccontextmanager
import logging

from app.api.v1 import api_router
from app.core.config import settings
from app.core.database import engine, Base
from app.services.execution_engine import execution_engine
from app.services.websocket_manager import ws_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager"""
    logger.info("Starting Automation Integration Engine...")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Start execution engine
    await execution_engine.start()
    
    yield
    
    # Cleanup
    await execution_engine.stop()
    logger.info("Automation Integration Engine stopped")

app = FastAPI(
    title="Automation Integration Engine",
    description="Production-grade workflow execution with security validation",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root_redirect():
    """Open root → show dashboard (easiest: just go to localhost:8000)."""
    return RedirectResponse(url="/dashboard", status_code=302)


@app.websocket("/ws/executions")
async def execution_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time execution updates"""
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for connection verification
            await websocket.send_text(f"Connected: {data}")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Avoid 404 when browser requests favicon."""
    return Response(status_code=204)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "automation-integration",
        "version": "1.0.0"
    }


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page():
    """Serve dashboard UI from backend (works without React frontend)."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Automation Integration Dashboard</title>
  <style>
    * { box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 24px; background: #f5f5f5; }
    h1 { margin: 0 0 24px; color: #1976d2; }
    .cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }
    .card { background: #fff; border-radius: 8px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); }
    .card .label { font-size: 12px; color: #666; text-transform: uppercase; margin-bottom: 4px; }
    .card .value { font-size: 28px; font-weight: 600; }
    .card.blue .value { color: #1976d2; }
    .card.green .value { color: #2e7d32; }
    .card.red .value { color: #c62828; }
    .card.orange .value { color: #ef6c00; }
    .section { background: #fff; border-radius: 8px; padding: 20px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); }
    .section h2 { margin: 0 0 16px; font-size: 18px; }
    .links { margin-top: 24px; }
    .links a { color: #1976d2; margin-right: 16px; }
    #error { color: #c62828; padding: 12px; background: #ffebee; border-radius: 8px; margin-bottom: 16px; display: none; }
  </style>
</head>
<body>
  <h1>Automation Integration Dashboard</h1>
  <div id="error"></div>
  <div class="cards">
    <div class="card blue"><div class="label">Total Executions</div><div class="value" id="total">-</div></div>
    <div class="card green"><div class="label">Completed</div><div class="value" id="completed">-</div></div>
    <div class="card red"><div class="label">Failed</div><div class="value" id="failed">-</div></div>
    <div class="card orange"><div class="label">Success Rate</div><div class="value" id="successRate">-</div></div>
  </div>
  <div class="section">
    <h2>Performance</h2>
    <p>Average execution time: <strong id="avgTime">-</strong>s &nbsp;|&nbsp; Running: <strong id="running">-</strong> &nbsp;|&nbsp; Pending: <strong id="pending">-</strong></p>
  </div>
  <div class="section">
    <h2>System</h2>
    <p>Status: <strong id="status">-</strong> &nbsp;|&nbsp; Active workers: <strong id="workers">-</strong> &nbsp;|&nbsp; Queue: <strong id="queue">-</strong></p>
  </div>
  <div class="links">
    <a href="/docs">API Docs</a>
    <a href="/api/v1/monitoring/metrics">Metrics JSON</a>
  </div>
  <script>
    const base = window.location.origin;
    async function load() {
      try {
        const [metrics, health] = await Promise.all([
          fetch(base + '/api/v1/monitoring/metrics').then(r => r.json()),
          fetch(base + '/api/v1/monitoring/health').then(r => r.json())
        ]);
        document.getElementById('total').textContent = metrics.total_executions;
        document.getElementById('completed').textContent = metrics.completed;
        document.getElementById('failed').textContent = metrics.failed;
        document.getElementById('successRate').textContent = (metrics.success_rate || 0).toFixed(1) + '%';
        document.getElementById('avgTime').textContent = (metrics.average_execution_time || 0).toFixed(2);
        document.getElementById('running').textContent = metrics.running;
        document.getElementById('pending').textContent = metrics.pending;
        document.getElementById('status').textContent = health.status || '-';
        document.getElementById('workers').textContent = health.active_workers ?? '-';
        document.getElementById('queue').textContent = health.queue_size ?? '-';
      } catch (e) {
        document.getElementById('error').textContent = 'Could not load data: ' + e.message;
        document.getElementById('error').style.display = 'block';
      }
    }
    load();
    setInterval(load, 5000);
  </script>
</body>
</html>"""
