from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.resource_service import ResourceService
from pydantic import BaseModel
from typing import Optional, Dict

router = APIRouter(prefix="/api/resources", tags=["resources"])

class ResourceCreate(BaseModel):
    resource_type: str
    cloud_provider: str
    region: str
    name: str
    tags: Optional[Dict] = {}
    config: Optional[Dict] = {}

class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[Dict] = None
    config: Optional[Dict] = None

@router.get("")
async def list_resources(
    resource_type: str = None,
    cloud_provider: str = None,
    status: str = None,
    search: str = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List resources with filtering and pagination"""
    filters = {k: v for k, v in {
        'resource_type': resource_type,
        'cloud_provider': cloud_provider,
        'status': status,
        'search': search
    }.items() if v}
    
    service = ResourceService(db)
    return await service.list_resources(filters, limit, offset)

@router.get("/{resource_id}")
async def get_resource(resource_id: str, db: AsyncSession = Depends(get_db)):
    """Get resource details"""
    service = ResourceService(db)
    resource = await service.get_resource(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource

@router.post("")
async def create_resource(resource: ResourceCreate, db: AsyncSession = Depends(get_db)):
    """Create new resource"""
    service = ResourceService(db)
    return await service.create_resource(resource.dict())

@router.patch("/{resource_id}")
async def update_resource(
    resource_id: str,
    updates: ResourceUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update resource"""
    service = ResourceService(db)
    updated = await service.update_resource(resource_id, updates.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Resource not found")
    return updated

@router.delete("/{resource_id}")
async def delete_resource(resource_id: str, db: AsyncSession = Depends(get_db)):
    """Delete resource"""
    service = ResourceService(db)
    success = await service.delete_resource(resource_id)
    if not success:
        raise HTTPException(status_code=404, detail="Resource not found")
    return {"message": "Resource deleted"}
