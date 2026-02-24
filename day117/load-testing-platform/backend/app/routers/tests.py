from fastapi import APIRouter, BackgroundTasks, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional
import asyncio, json
from app.services import runner

router = APIRouter(prefix="/api/tests", tags=["tests"])

class TestConfig(BaseModel):
    name: str = "Load Test Run"
    test_type: str = "load"  # load | benchmark | stress
    target_url: str = "http://localhost:8117"
    users: int = 10
    spawn_rate: float = 1.0
    duration_seconds: int = 30
    error_threshold_percent: float = 5.0

@router.post("/start")
async def start_test(config: TestConfig):
    run_id = await runner.start_test_run(config.model_dump())
    return {"run_id": run_id, "status": "started", "config": config.model_dump()}

@router.get("/runs")
async def list_runs():
    return {"runs": runner.get_all_runs()}

@router.get("/runs/{run_id}")
async def get_run(run_id: str):
    run = runner.get_run(run_id)
    if not run:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Run not found")
    return run

@router.websocket("/ws/{run_id}")
async def websocket_metrics(websocket: WebSocket, run_id: str):
    await websocket.accept()

    async def send_metric(data: dict):
        try:
            await websocket.send_text(json.dumps(data))
        except Exception:
            pass

    runner.register_metric_callback(run_id, send_metric)

    # Send current state immediately
    run = runner.get_run(run_id)
    if run:
        await websocket.send_text(json.dumps({"type": "init", "run": run}))

    try:
        while True:
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=30)
            except asyncio.TimeoutError:
                await websocket.send_text(json.dumps({"type": "ping"}))
    except WebSocketDisconnect:
        pass
    finally:
        runner.unregister_metric_callback(run_id, send_metric)
