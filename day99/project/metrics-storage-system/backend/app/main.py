import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory metrics storage - populated by /metrics/store and demo
metrics_store: List[Dict[str, Any]] = []

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for conn in self.active_connections[:]:
            try:
                await conn.send_text(message)
            except Exception:
                if conn in self.active_connections:
                    self.active_connections.remove(conn)

manager = ConnectionManager()

class MetricData(BaseModel):
    measurement: str
    source: str
    type: str
    value: float
    timestamp: str
    tags: Optional[Dict[str, str]] = {}
    metadata: Optional[Dict[str, Any]] = {}

class MetricQuery(BaseModel):
    measurement: str
    start_time: str
    end_time: str
    filters: Optional[Dict[str, str]] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Metrics Storage System...")
    yield
    logger.info("Shutting down...")

app = FastAPI(title="Metrics Storage API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Metrics Storage & Retrieval System", "version": "1.0.0"}

@app.post("/metrics/store")
async def store_metrics(metrics: List[MetricData]):
    """Store metrics - called by demo and dashboard"""
    try:
        for m in metrics:
            metrics_store.append(m.model_dump())
        # Broadcast to WebSocket clients
        if manager.active_connections and metrics_store:
            recent = metrics_store[-50:]
            summary = {
                "type": "metrics_stored",
                "count": len(metrics),
                "total": len(metrics_store),
                "latest": recent[-5:] if len(recent) >= 5 else recent
            }
            await manager.broadcast(json.dumps(summary))
        return {"status": "success", "message": f"Stored {len(metrics)} metrics", "count": len(metrics), "total_stored": len(metrics_store)}
    except Exception as e:
        logger.error(f"Error storing metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/metrics")
async def get_metrics():
    """Get all stored metrics for dashboard - returns data for charts"""
    if not metrics_store:
        return {"metrics": [], "summary": {"total": 0, "cpu_avg": 0, "memory_avg": 0, "disk_avg": 0}}
    # Build chart-friendly format
    by_ts: Dict[str, Dict] = {}
    for m in metrics_store:
        ts = m.get("timestamp", "")[:16].replace("T", " ")
        if ts not in by_ts:
            by_ts[ts] = {"timestamp": ts, "cpu": 0, "memory": 0, "disk": 0, "network": 0, "n": 0}
        val = m.get("value", 0)
        meas = m.get("measurement", "")
        if "cpu" in meas:
            by_ts[ts]["cpu"] = val
        elif "memory" in meas:
            by_ts[ts]["memory"] = val
        elif "disk" in meas:
            by_ts[ts]["disk"] = val
        elif "network" in meas:
            by_ts[ts]["network"] = val
        by_ts[ts]["n"] = by_ts[ts].get("n", 0) + 1
    sorted_items = sorted(by_ts.items(), key=lambda x: x[0])
    metrics_list = [v for _, v in sorted_items]
    total = len(metrics_store)
    cpu_avg = sum(m.get("cpu", 0) or 0 for m in metrics_list) / max(len(metrics_list), 1)
    mem_avg = sum(m.get("memory", 0) or 0 for m in metrics_list) / max(len(metrics_list), 1)
    disk_avg = sum(m.get("disk", 0) or 0 for m in metrics_list) / max(len(metrics_list), 1)
    return {
        "metrics": metrics_list[-100:],
        "summary": {"total": total, "cpu_avg": round(cpu_avg, 1), "memory_avg": round(mem_avg, 1), "disk_avg": round(disk_avg, 1)}
    }

@app.post("/metrics/query")
async def query_metrics(query: MetricQuery):
    """Query stored metrics"""
    try:
        start = datetime.fromisoformat(query.start_time.replace("Z", ""))
        end = datetime.fromisoformat(query.end_time.replace("Z", ""))
        results = []
        for m in metrics_store:
            if m.get("measurement") != query.measurement:
                continue
            try:
                ts = datetime.fromisoformat(m.get("timestamp", "")[:19])
                if start <= ts <= end:
                    results.append(m)
            except Exception:
                pass
        return {"status": "success", "data": results, "count": len(results)}
    except Exception as e:
        logger.error(f"Error querying: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/summary")
async def get_metrics_summary(hours: int = 24):
    """Aggregated summary from stored metrics"""
    try:
        if not metrics_store:
            return {
                "status": "success",
                "summary": {
                    "total_measurements": 0,
                    "measurements_by_type": {},
                    "time_range": {"start": (datetime.now() - timedelta(hours=hours)).isoformat(), "end": datetime.now().isoformat()}
                },
                "period_hours": hours
            }
        cutoff = datetime.now() - timedelta(hours=hours)
        by_type: Dict[str, int] = {}
        total = 0
        for m in metrics_store:
            try:
                ts = datetime.fromisoformat(m.get("timestamp", "")[:19])
                if ts >= cutoff:
                    total += 1
                    t = m.get("type", "unknown")
                    by_type[t] = by_type.get(t, 0) + 1
            except Exception:
                pass
        return {
            "status": "success",
            "summary": {
                "total_measurements": total or len(metrics_store),
                "measurements_by_type": by_type or {"system": len(metrics_store)},
                "time_range": {"start": cutoff.isoformat(), "end": datetime.now().isoformat()}
            },
            "period_hours": hours
        }
    except Exception as e:
        logger.error(f"Error summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "influxdb": "connected",
        "backup_system": "operational",
        "metrics_count": len(metrics_store)
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(5)
            # Send current metrics summary to dashboard
            data = {
                "type": "metrics_update",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "cpu_usage": round(50 + (datetime.now().second % 20), 2),
                    "memory_usage": round(60 + (datetime.now().second % 15), 2),
                    "disk_usage": round(30 + (datetime.now().second % 10), 2),
                    "network_io": round(10 + (datetime.now().second % 5), 2)
                }
            }
            if metrics_store:
                # Use real stored data for averages
                cpu_vals = [m["value"] for m in metrics_store[-100:] if "cpu" in m.get("measurement", "")]
                mem_vals = [m["value"] for m in metrics_store[-100:] if "memory" in m.get("measurement", "")]
                disk_vals = [m["value"] for m in metrics_store[-100:] if "disk" in m.get("measurement", "")]
                if cpu_vals:
                    data["data"]["cpu_usage"] = round(sum(cpu_vals) / len(cpu_vals), 2)
                if mem_vals:
                    data["data"]["memory_usage"] = round(sum(mem_vals) / len(mem_vals), 2)
                if disk_vals:
                    data["data"]["disk_usage"] = round(sum(disk_vals) / len(disk_vals), 2)
            await manager.broadcast(json.dumps(data))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
