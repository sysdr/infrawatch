from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.cost_service import CostService

router = APIRouter(prefix="/api/costs", tags=["costs"])

@router.get("/summary")
async def get_cost_summary(days: int = 30, db: AsyncSession = Depends(get_db)):
    """Get cost summary for period"""
    service = CostService(db)
    return await service.get_cost_summary(days)

@router.get("/trends")
async def get_cost_trends(days: int = 90, db: AsyncSession = Depends(get_db)):
    """Get cost trends over time"""
    service = CostService(db)
    return await service.get_cost_trends(days)

@router.get("/forecast")
async def forecast_costs(days: int = 30, db: AsyncSession = Depends(get_db)):
    """Forecast future costs"""
    service = CostService(db)
    return await service.forecast_costs(days)

@router.get("/top-resources")
async def get_top_resources(limit: int = 10, db: AsyncSession = Depends(get_db)):
    """Get most expensive resources"""
    service = CostService(db)
    return await service.get_top_resources_by_cost(limit)
