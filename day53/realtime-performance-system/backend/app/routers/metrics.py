from fastapi import APIRouter
from ..services.metrics_collector import metrics_collector

router = APIRouter()

@router.get("/current")
async def get_current_metrics():
    """Get current system metrics"""
    return metrics_collector.get_current_metrics()

@router.get("/history")
async def get_metrics_history():
    """Get metrics history (last 60 seconds)"""
    return {
        "metrics": metrics_collector.get_metrics_history(),
        "count": len(metrics_collector.get_metrics_history())
    }
