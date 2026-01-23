from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from app.utils.database import get_db
from app.models.resource import Resource

router = APIRouter()

@router.get("/resources")
async def list_resources(
    resource_type: Optional[str] = None,
    provider: Optional[str] = None,
    region: Optional[str] = None,
    limit: int = Query(100, le=1000),
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List all discovered resources"""
    query = select(Resource)
    
    if resource_type:
        query = query.where(Resource.resource_type == resource_type)
    if provider:
        query = query.where(Resource.provider == provider)
    if region:
        query = query.where(Resource.region == region)
    
    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    resources = result.scalars().all()
    
    return {
        "resources": [
            {
                "id": r.id,
                "type": r.resource_type,
                "name": r.name,
                "provider": r.provider,
                "region": r.region,
                "state": r.state,
                "discovered_at": r.discovered_at.isoformat(),
                "metadata": r.resource_metadata
            }
            for r in resources
        ],
        "total": len(resources)
    }

@router.get("/resources/{resource_id}")
async def get_resource(resource_id: str, db: AsyncSession = Depends(get_db)):
    """Get specific resource details"""
    result = await db.execute(
        select(Resource).where(Resource.id == resource_id)
    )
    resource = result.scalar_one_or_none()
    
    if not resource:
        return {"error": "Resource not found"}
    
    return {
        "id": resource.id,
        "type": resource.resource_type,
        "name": resource.name,
        "provider": resource.provider,
        "region": resource.region,
        "state": resource.state,
        "config_hash": resource.config_hash,
        "discovered_at": resource.discovered_at.isoformat(),
        "updated_at": resource.updated_at.isoformat(),
        "metadata": resource.resource_metadata
    }

@router.get("/stats")
async def inventory_stats(db: AsyncSession = Depends(get_db)):
    """Get inventory statistics"""
    # Count by type
    result = await db.execute(
        select(Resource.resource_type, func.count(Resource.id))
        .group_by(Resource.resource_type)
    )
    type_counts = dict(result.all())
    
    # Count by provider
    result = await db.execute(
        select(Resource.provider, func.count(Resource.id))
        .group_by(Resource.provider)
    )
    provider_counts = dict(result.all())
    
    # Total count
    result = await db.execute(select(func.count(Resource.id)))
    total = result.scalar()
    
    return {
        "total_resources": total,
        "by_type": type_counts,
        "by_provider": provider_counts
    }
