from fastapi import APIRouter, Depends
from typing import List, Dict
import json
from app.services.collector_manager import CollectorManager

router = APIRouter()

async def get_collector_manager() -> CollectorManager:
    from app.main import collector_manager
    return collector_manager

@router.get("/metrics/{resource_id}")
async def get_resource_health(
    resource_id: str,
    manager: CollectorManager = Depends(get_collector_manager)
):
    """Get health metrics for a specific resource"""
    data = await manager.redis.get(f"health:{resource_id}")
    
    if not data:
        return {"error": "Health metrics not found"}
    
    return json.loads(data)

@router.get("/summary")
async def get_health_summary(manager: CollectorManager = Depends(get_collector_manager)):
    """Get overall health summary"""
    resources = await manager.get_all_resources()
    
    summary = {
        'total_resources': len(resources),
        'healthy': 0,
        'degraded': 0,
        'unhealthy': 0,
        'unknown': 0
    }
    
    for resource in resources:
        health_data = await manager.redis.get(f"health:{resource['resource_id']}")
        
        if health_data:
            health = json.loads(health_data)
            status = health.get('health_status', 'unknown')
            summary[status] = summary.get(status, 0) + 1
        else:
            summary['unknown'] += 1
    
    return summary
