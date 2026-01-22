from fastapi import APIRouter, Depends
from typing import List, Dict
from datetime import datetime, timedelta
from app.services.collector_manager import CollectorManager

router = APIRouter()

async def get_collector_manager() -> CollectorManager:
    from app.main import collector_manager
    return collector_manager

@router.get("/current", response_model=List[Dict])
async def get_current_costs(manager: CollectorManager = Depends(get_collector_manager)):
    """Get current resource costs"""
    return await manager.get_resource_costs()

@router.get("/summary")
async def get_cost_summary(manager: CollectorManager = Depends(get_collector_manager)):
    """Get cost summary and breakdown"""
    costs = await manager.get_resource_costs()
    
    total = sum(c['cost_usd'] for c in costs)
    
    by_type = {}
    by_region = {}
    
    for cost in costs:
        # By type
        rtype = cost['resource_type']
        by_type[rtype] = by_type.get(rtype, 0) + cost['cost_usd']
        
        # By region
        region = cost['region']
        by_region[region] = by_region.get(region, 0) + cost['cost_usd']
    
    return {
        'total_cost_usd': round(total, 2),
        'by_type': {k: round(v, 2) for k, v in by_type.items()},
        'by_region': {k: round(v, 2) for k, v in by_region.items()},
        'timestamp': datetime.utcnow().isoformat()
    }

@router.get("/forecast")
async def get_cost_forecast(
    days: int = 30,
    manager: CollectorManager = Depends(get_collector_manager)
):
    """Get cost forecast"""
    return await manager.cost_calculator.get_cost_forecast(days)
