from fastapi import APIRouter, Depends
from typing import List, Dict
from app.services.collector_manager import CollectorManager

router = APIRouter()

async def get_collector_manager() -> CollectorManager:
    from app.main import collector_manager
    return collector_manager

@router.get("/", response_model=List[Dict])
async def get_resources(
    resource_type: str = None,
    region: str = None,
    manager: CollectorManager = Depends(get_collector_manager)
):
    """Get all resources with optional filtering"""
    resources = await manager.get_all_resources()
    
    if resource_type:
        resources = [r for r in resources if r['resource_type'] == resource_type]
    
    if region:
        resources = [r for r in resources if r['region'] == region]
    
    return resources

@router.get("/summary")
async def get_resources_summary(manager: CollectorManager = Depends(get_collector_manager)):
    """Get resource count summary"""
    resources = await manager.get_all_resources()
    
    summary = {
        'total': len(resources),
        'by_type': {},
        'by_region': {},
        'by_state': {}
    }
    
    for resource in resources:
        # By type
        rtype = resource['resource_type']
        summary['by_type'][rtype] = summary['by_type'].get(rtype, 0) + 1
        
        # By region
        region = resource['region']
        summary['by_region'][region] = summary['by_region'].get(region, 0) + 1
        
        # By state
        state = resource.get('state', 'unknown')
        summary['by_state'][state] = summary['by_state'].get(state, 0) + 1
    
    return summary
