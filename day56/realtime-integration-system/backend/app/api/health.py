from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Real-time Integration System"
    }

@router.get("/metrics")
async def get_metrics():
    """Get system metrics"""
    from app.main import metrics_collector
    
    if metrics_collector:
        return metrics_collector.get_summary()
    return {"error": "Metrics not available"}
