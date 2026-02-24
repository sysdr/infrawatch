from fastapi import APIRouter
from app.services.metrics import metrics_sampler, collect_system_metrics

router = APIRouter(prefix="/api/system", tags=["system"])

@router.get("/metrics")
async def get_metrics():
    return collect_system_metrics()

@router.get("/snapshot")
async def get_snapshot():
    return metrics_sampler.latest or collect_system_metrics()
