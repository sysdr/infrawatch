from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models import Dashboard, Widget
from app.schemas import DashboardCreate, DashboardUpdate, DashboardResponse
from typing import List

router = APIRouter()

@router.post("/", response_model=DashboardResponse)
async def create_dashboard(dashboard: DashboardCreate, db: AsyncSession = Depends(get_db)):
    db_dashboard = Dashboard(**dashboard.model_dump())
    db.add(db_dashboard)
    await db.commit()
    await db.refresh(db_dashboard)
    return db_dashboard

@router.get("/", response_model=List[DashboardResponse])
async def get_dashboards(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Dashboard).order_by(Dashboard.created_at.desc()))
    return result.scalars().all()

@router.get("/{dashboard_id}", response_model=DashboardResponse)
async def get_dashboard(dashboard_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Dashboard).where(Dashboard.id == dashboard_id))
    dashboard = result.scalar_one_or_none()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return dashboard

@router.put("/{dashboard_id}", response_model=DashboardResponse)
async def update_dashboard(dashboard_id: str, dashboard: DashboardUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Dashboard).where(Dashboard.id == dashboard_id))
    db_dashboard = result.scalar_one_or_none()
    if not db_dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    update_data = dashboard.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_dashboard, key, value)
    
    await db.commit()
    await db.refresh(db_dashboard)
    return db_dashboard

@router.delete("/{dashboard_id}")
async def delete_dashboard(dashboard_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Dashboard).where(Dashboard.id == dashboard_id))
    dashboard = result.scalar_one_or_none()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    await db.delete(dashboard)
    await db.commit()
    return {"message": "Dashboard deleted successfully"}
