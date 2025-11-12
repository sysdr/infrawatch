from fastapi import APIRouter, HTTPException
from typing import Dict

router = APIRouter()

@router.get("/current")
async def get_current_metrics() -> Dict:
    """Get current system metrics snapshot"""
    from app.services.metric_collector import MetricCollector
    # This would ideally use dependency injection
    return {"status": "streaming", "message": "Use WebSocket for real-time metrics"}

@router.get("/stats")
async def get_stats() -> Dict:
    """Get streaming statistics"""
    from app.main import stream_manager, metric_collector
    return {
        'stream_stats': stream_manager.get_stats(),
        'metrics_collected': metric_collector.total_collected
    }
