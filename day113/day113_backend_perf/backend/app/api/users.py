from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.user_service import get_users_paginated, get_team_user_counts
from app.services.cache import cache_service
router = APIRouter(prefix="/users", tags=["users"])
@router.get("")
async def list_users(team_id: str | None = Query(None), after: str | None = Query(None), fields: str | None = Query(None), db: AsyncSession = Depends(get_db)):
    field_list = fields.split(",") if fields else None
    result = await get_users_paginated(db, team_id, after, field_list)
    return result
@router.get("/team-analytics")
async def team_analytics(db: AsyncSession = Depends(get_db)):
    data = await get_team_user_counts(db)
    return {"data": data, "cache_stats": cache_service.stats}
@router.delete("/cache/invalidate")
async def invalidate_cache(tag: str = Query(...)):
    deleted = await cache_service.delete_by_tag(tag)
    return {"deleted_keys": deleted, "tag": tag}
