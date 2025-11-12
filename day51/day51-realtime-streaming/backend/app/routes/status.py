from fastapi import APIRouter
from typing import Dict
from enum import Enum

router = APIRouter()

class ServiceStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    RECOVERING = "recovering"

@router.get("/services")
async def get_service_status() -> Dict:
    """Get status of all services"""
    return {
        'streaming_service': ServiceStatus.HEALTHY.value,
        'metric_collector': ServiceStatus.HEALTHY.value,
        'alert_service': ServiceStatus.HEALTHY.value,
        'websocket_server': ServiceStatus.HEALTHY.value
    }
