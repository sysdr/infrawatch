from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.team import (
    TeamCreate, TeamResponse, TeamMemberAdd, TeamMemberResponse,
    TeamDashboardMetrics, OrganizationCreate, RoleCreate
)
from app.services.team_service import TeamService
from app.models.team import Organization, Role
from typing import List

router = APIRouter(prefix="/api/teams", tags=["teams"])

@router.post("/organizations", response_model=dict)
async def create_organization(org: OrganizationCreate, db: AsyncSession = Depends(get_db)):
    try:
        org_obj = Organization(**org.model_dump())
        db.add(org_obj)
        await db.commit()
        await db.refresh(org_obj)
        return {"id": org_obj.id, "name": org_obj.name, "slug": org_obj.slug}
    except Exception as e:
        await db.rollback()
        error_msg = str(e)
        if "duplicate key" in error_msg.lower() or "unique constraint" in error_msg.lower():
            raise HTTPException(status_code=400, detail=f"Organization with slug '{org.slug}' already exists. Please use a different slug.")
        raise HTTPException(status_code=500, detail=f"Failed to create organization: {error_msg}")

@router.post("/roles", response_model=dict)
async def create_role(role: RoleCreate, db: AsyncSession = Depends(get_db)):
    try:
        role_obj = Role(**role.model_dump())
        db.add(role_obj)
        await db.commit()
        await db.refresh(role_obj)
        return {"id": role_obj.id, "name": role_obj.name}
    except Exception as e:
        await db.rollback()
        error_msg = str(e)
        if "duplicate key" in error_msg.lower() or "unique constraint" in error_msg.lower():
            raise HTTPException(status_code=400, detail=f"Role with name '{role.name}' may already exist. Please use a different name.")
        raise HTTPException(status_code=500, detail=f"Failed to create role: {error_msg}")

@router.post("", response_model=TeamResponse)
async def create_team(team: TeamCreate, db: AsyncSession = Depends(get_db)):
    try:
        service = TeamService(db)
        # Mock creator_id for demo
        creator_id = 1
        team_obj = await service.create_team(team, creator_id)
        # Convert team_metadata to metadata for response
        # Handle the case where team_metadata might be None or a MetaData object
        metadata_value = {}
        if hasattr(team_obj, 'team_metadata'):
            if team_obj.team_metadata is None:
                metadata_value = {}
            elif isinstance(team_obj.team_metadata, dict):
                metadata_value = team_obj.team_metadata
            else:
                # If it's a MetaData object or something else, convert to dict
                metadata_value = dict(team_obj.team_metadata) if hasattr(team_obj.team_metadata, '__dict__') else {}
        
        team_dict = {
            "id": team_obj.id,
            "organization_id": team_obj.organization_id,
            "name": team_obj.name,
            "slug": team_obj.slug,
            "description": team_obj.description,
            "parent_team_id": team_obj.parent_team_id,
            "materialized_path": team_obj.materialized_path,
            "member_count": team_obj.member_count or 0,
            "last_activity_at": team_obj.last_activity_at,
            "created_at": team_obj.created_at,
            "metadata": metadata_value
        }
        return TeamResponse(**team_dict)
    except Exception as e:
        await db.rollback()
        error_msg = str(e)
        raise HTTPException(status_code=500, detail=f"Failed to create team: {error_msg}")

@router.post("/{team_id}/members", response_model=TeamMemberResponse)
async def add_team_member(team_id: int, member: TeamMemberAdd, db: AsyncSession = Depends(get_db)):
    service = TeamService(db)
    # Mock inviter_id for demo
    inviter_id = 1
    member_obj = await service.add_team_member(team_id, member.user_id, member.role_id, inviter_id)
    return member_obj

@router.get("/{team_id}/dashboard", response_model=TeamDashboardMetrics)
async def get_team_dashboard(team_id: int, db: AsyncSession = Depends(get_db)):
    service = TeamService(db)
    return await service.get_team_dashboard(team_id)

@router.get("/{team_id}/permissions")
async def get_team_permissions(team_id: int, user_id: int, db: AsyncSession = Depends(get_db)):
    # Simplified permission check
    return {"team_id": team_id, "user_id": user_id, "permissions": ["read", "write"]}

@router.get("/{team_id}/members", response_model=List[TeamMemberResponse])
async def get_team_members(team_id: int, db: AsyncSession = Depends(get_db)):
    from app.models.team import TeamMember
    from sqlalchemy import select
    
    result = await db.execute(
        select(TeamMember).where(TeamMember.team_id == team_id).order_by(TeamMember.joined_at)
    )
    members = result.scalars().all()
    return [TeamMemberResponse(
        id=m.id,
        team_id=m.team_id,
        user_id=m.user_id,
        role_id=m.role_id,
        joined_at=m.joined_at,
        effective_permissions=m.effective_permissions or []
    ) for m in members]
