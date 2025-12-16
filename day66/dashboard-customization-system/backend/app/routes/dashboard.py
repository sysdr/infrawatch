from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.auth import get_current_user
from app.schemas import (
    DashboardCreate, DashboardUpdate, DashboardResponse,
    ShareCreate, ShareResponse
)
from app.services.dashboard_service import DashboardService
from typing import List
from uuid import UUID

router = APIRouter(prefix="/api/dashboards", tags=["dashboards"])

@router.post("", response_model=DashboardResponse)
async def create_dashboard(
    dashboard: DashboardCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    db_dashboard = await DashboardService.create_dashboard(
        db, dashboard, UUID(current_user["id"])
    )
    return db_dashboard

@router.get("/{dashboard_id}", response_model=DashboardResponse)
async def get_dashboard(
    dashboard_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    dashboard = await DashboardService.get_dashboard(db, dashboard_id, UUID(current_user["id"]))
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return dashboard

@router.put("/{dashboard_id}", response_model=DashboardResponse)
async def update_dashboard(
    dashboard_id: UUID,
    update: DashboardUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        dashboard = await DashboardService.update_dashboard(
            db, dashboard_id, update, UUID(current_user["id"])
        )
        if not dashboard:
            raise HTTPException(status_code=404, detail="Dashboard not found")
        return dashboard
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.get("", response_model=List[DashboardResponse])
async def list_dashboards(
    is_template: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    dashboards = await DashboardService.list_dashboards(
        db, UUID(current_user["id"]), is_template
    )
    return dashboards

@router.get("/templates/list", response_model=List[DashboardResponse])
async def list_templates(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    templates = await DashboardService.list_templates(db)
    return templates

@router.post("/{dashboard_id}/share", response_model=ShareResponse)
async def create_share(
    dashboard_id: UUID,
    share: ShareCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Verify dashboard exists and user owns it
    dashboard = await DashboardService.get_dashboard(db, dashboard_id, UUID(current_user["id"]))
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    share_obj = await DashboardService.create_share(
        db, dashboard_id, share.permission, share.expires_in_hours, UUID(current_user["id"])
    )
    return share_obj

@router.get("/{dashboard_id}/shares", response_model=List[ShareResponse])
async def list_shares(
    dashboard_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Verify dashboard exists and user owns it
    dashboard = await DashboardService.get_dashboard(db, dashboard_id, UUID(current_user["id"]))
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    shares = await DashboardService.list_shares(db, dashboard_id)
    return shares

@router.delete("/shares/{share_id}")
async def revoke_share(
    share_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    success = await DashboardService.revoke_share(db, share_id)
    if not success:
        raise HTTPException(status_code=404, detail="Share not found")
    return {"message": "Share revoked successfully"}

@router.get("/shared/{share_token}", response_model=DashboardResponse)
async def get_shared_dashboard(
    share_token: str,
    db: AsyncSession = Depends(get_db)
):
    share = await DashboardService.get_share(db, share_token)
    if not share:
        raise HTTPException(status_code=404, detail="Invalid or expired share link")
    
    dashboard = await DashboardService.get_dashboard(db, share.dashboard_id)
    return dashboard
