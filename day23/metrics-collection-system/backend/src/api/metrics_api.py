from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

metrics_router = APIRouter()

# Global components (will be injected)
components = {}

class MetricData(BaseModel):
    name: str
    value: float
    unit: str
    timestamp: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = {}

@metrics_router.get("/stats")
async def get_system_stats():
    """Get overall system statistics"""
    try:
        return {
            "status": "running",
            "ingestion": components.get("ingester", {}).get_stats() if "ingester" in components else {},
            "processing": components.get("processor", {}).get_batch_stats() if "processor" in components else {},
            "validation": components.get("validator", {}).get_validation_stats() if "validator" in components else {},
            "agents": components.get("protocol", {}).get_agent_stats() if "protocol" in components else {}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@metrics_router.get("/metrics/recent")
async def get_recent_metrics(limit: int = 100):
    """Get recently collected metrics"""
    try:
        if "ingester" in components:
            return components["ingester"].get_recent_metrics(limit)
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@metrics_router.get("/agents")
async def get_agent_status():
    """Get status of connected agents"""
    try:
        if "protocol" in components:
            return components["protocol"].get_agent_stats()
        return {"connected_agents": 0, "agents": {}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@metrics_router.get("/schedules")
async def get_collection_schedules():
    """Get current collection schedules"""
    try:
        if "scheduler" in components:
            return components["scheduler"].get_schedules()
        return {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@metrics_router.post("/validate")
async def validate_metric(metric: MetricData):
    """Validate a metric manually"""
    try:
        if "validator" in components:
            is_valid = await components["validator"].validate_metric(metric.dict())
            return {"valid": is_valid}
        return {"valid": False, "error": "Validator not available"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
