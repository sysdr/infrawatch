from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.topology_service import TopologyService

router = APIRouter(prefix="/api/topology", tags=["topology"])

@router.get("")
async def get_topology(
    cloud_provider: str = None,
    region: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Get infrastructure topology graph"""
    filters = {}
    if cloud_provider:
        filters['cloud_provider'] = cloud_provider
    if region:
        filters['region'] = region
    
    service = TopologyService(db)
    topology = await service.get_topology(filters)
    return topology
