from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.permission_service import PermissionService
from app.schemas.permission import UserPermissionCreate, TeamPermissionCreate, PermissionResponse
from app.models.permission import PermissionType

router = APIRouter()

@router.post("/users", response_model=PermissionResponse)
def grant_user_permission(perm: UserPermissionCreate, db: Session = Depends(get_db)):
    return PermissionService.grant_user_permission(db, perm)

@router.post("/teams", response_model=PermissionResponse)
def grant_team_permission(perm: TeamPermissionCreate, db: Session = Depends(get_db)):
    return PermissionService.grant_team_permission(db, perm)

@router.get("/users/{user_id}")
def get_user_permissions(user_id: int, db: Session = Depends(get_db)):
    return PermissionService.get_user_permissions(db, user_id)

@router.post("/check")
def check_permission(
    user_id: int,
    resource_type: str,
    resource_id: str,
    permission_type: PermissionType,
    db: Session = Depends(get_db)
):
    has_permission = PermissionService.check_permission(
        db, user_id, resource_type, resource_id, permission_type
    )
    return {"has_permission": has_permission}
