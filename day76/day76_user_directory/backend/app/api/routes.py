from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import io

from ..database import get_db
from ..models import User, LDAPConfig, SAMLConfig, ImportJob, UserStatus
from ..schemas import (UserResponse, UserCreate, UserUpdate, LDAPConfigCreate, 
                       LDAPConfigResponse, ImportStatus)
from ..services.ldap_service import LDAPService
from ..services.saml_service import SAMLService
from ..services.lifecycle_service import LifecycleService
from ..services.import_export_service import ImportExportService

router = APIRouter()

# User CRUD
@router.get("/users", response_model=List[UserResponse])
def list_users(
    status: Optional[UserStatus] = None,
    department: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(User)
    if status:
        query = query.filter(User.status == status)
    if department:
        query = query.filter(User.department == department)
    return query.offset(skip).limit(limit).all()

@router.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Import/Export - Must be defined before /users/{user_id} to avoid route conflicts
@router.post("/users/import", response_model=ImportStatus)
async def import_users(
    file: UploadFile = File(...),
    update_existing: bool = False,
    db: Session = Depends(get_db)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    content = await file.read()
    csv_content = content.decode('utf-8')
    
    service = ImportExportService(db)
    job = service.import_users_from_csv(csv_content, "admin", update_existing)
    
    return ImportStatus(
        job_id=job.id,
        total_users=job.total_users,
        processed=job.processed,
        created_count=job.created_count,
        updated_count=job.updated_count,
        failed_count=job.failed_count,
        status=job.status
    )

@router.get("/users/export")
def export_users(
    status: Optional[UserStatus] = None,
    department: Optional[str] = None,
    db: Session = Depends(get_db)
):
    filters = {}
    if status:
        filters['status'] = status
    if department:
        filters['department'] = department
    
    service = ImportExportService(db)
    csv_content = service.export_users_to_csv(filters)
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=users_export.csv"}
    )

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user

# LDAP Integration
@router.post("/ldap/configs", response_model=LDAPConfigResponse)
def create_ldap_config(config: LDAPConfigCreate, db: Session = Depends(get_db)):
    db_config = LDAPConfig(**config.dict())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

@router.get("/ldap/configs", response_model=List[LDAPConfigResponse])
def list_ldap_configs(db: Session = Depends(get_db)):
    return db.query(LDAPConfig).all()

@router.post("/ldap/sync/{config_id}")
def sync_ldap(config_id: int, db: Session = Depends(get_db)):
    config = db.query(LDAPConfig).filter(LDAPConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="LDAP config not found")
    
    ldap_service = LDAPService()
    stats = ldap_service.sync_users(config, db)
    
    return {
        "message": "Sync completed",
        "stats": stats,
        "sync_time": datetime.utcnow()
    }

@router.post("/ldap/authenticate")
def ldap_authenticate(username: str, password: str, db: Session = Depends(get_db)):
    config = db.query(LDAPConfig).filter(LDAPConfig.is_active == True).first()
    if not config:
        raise HTTPException(status_code=400, detail="No active LDAP configuration")
    
    ldap_service = LDAPService()
    user_data = ldap_service.authenticate(username, password, config)
    
    if not user_data:
        raise HTTPException(status_code=401, detail="Authentication failed")
    
    # Update or create user
    user = db.query(User).filter(User.username == username).first()
    if user:
        user.last_login = datetime.utcnow()
        db.commit()
    
    return {
        "authenticated": True,
        "user": user_data,
        "message": "LDAP authentication successful"
    }

# SSO/SAML
@router.get("/saml/login")
def saml_login(db: Session = Depends(get_db)):
    config = db.query(SAMLConfig).filter(SAMLConfig.is_active == True).first()
    if not config:
        raise HTTPException(status_code=400, detail="No active SAML configuration")
    
    saml_service = SAMLService()
    authn_request = saml_service.generate_authn_request(config.sso_url)
    
    return {
        "sso_url": config.sso_url,
        "saml_request": authn_request,
        "relay_state": "initial_login"
    }

@router.post("/saml/acs")
def saml_acs(saml_response: str, db: Session = Depends(get_db)):
    """Assertion Consumer Service - handles SAML response"""
    saml_service = SAMLService()
    user_data = saml_service.parse_saml_response(saml_response)
    
    if not user_data:
        raise HTTPException(status_code=400, detail="Invalid SAML response")
    
    # Check if user exists
    user = db.query(User).filter(User.email == user_data['email']).first()
    
    config = db.query(SAMLConfig).filter(SAMLConfig.is_active == True).first()
    
    if not user and config and config.jit_provisioning:
        # Just-in-Time provisioning
        user = saml_service.create_jit_user(user_data, db)
        return {
            "authenticated": True,
            "user_created": True,
            "user": {"id": user.id, "username": user.username, "email": user.email}
        }
    elif user:
        user.last_login = datetime.utcnow()
        db.commit()
        return {
            "authenticated": True,
            "user_created": False,
            "user": {"id": user.id, "username": user.username, "email": user.email}
        }
    else:
        raise HTTPException(status_code=403, detail="User not found and JIT provisioning disabled")

# Import/Export
@router.post("/users/import", response_model=ImportStatus)
async def import_users(
    file: UploadFile = File(...),
    update_existing: bool = False,
    db: Session = Depends(get_db)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    content = await file.read()
    csv_content = content.decode('utf-8')
    
    service = ImportExportService(db)
    job = service.import_users_from_csv(csv_content, "admin", update_existing)
    
    return ImportStatus(
        job_id=job.id,
        total_users=job.total_users,
        processed=job.processed,
        created_count=job.created_count,
        updated_count=job.updated_count,
        failed_count=job.failed_count,
        status=job.status
    )

@router.get("/users/export")
def export_users(
    status: Optional[UserStatus] = None,
    department: Optional[str] = None,
    db: Session = Depends(get_db)
):
    filters = {}
    if status:
        filters['status'] = status
    if department:
        filters['department'] = department
    
    service = ImportExportService(db)
    csv_content = service.export_users_to_csv(filters)
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=users_export.csv"}
    )

# Lifecycle Management
@router.post("/users/{user_id}/lifecycle/transition")
def transition_user_status(
    user_id: int,
    new_status: UserStatus,
    reason: str = "",
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    lifecycle_service = LifecycleService(db)
    result = lifecycle_service.transition_user(user, new_status, "admin", reason)
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])
    
    return result

@router.post("/users/{user_id}/lifecycle/offboard")
def offboard_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    lifecycle_service = LifecycleService(db)
    result = lifecycle_service.process_offboarding(user, "admin")
    
    return result

# Statistics
@router.get("/stats/overview")
def get_stats(db: Session = Depends(get_db)):
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.status == UserStatus.ACTIVE).count()
    pending_users = db.query(User).filter(User.status == UserStatus.PENDING).count()
    suspended_users = db.query(User).filter(User.status == UserStatus.SUSPENDED).count()
    ldap_synced = db.query(User).filter(User.is_ldap_synced == True).count()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "pending_users": pending_users,
        "suspended_users": suspended_users,
        "ldap_synced_users": ldap_synced,
        "provisioning_breakdown": {
            "manual": db.query(User).filter(User.provisioning_method == "manual").count(),
            "ldap_sync": db.query(User).filter(User.provisioning_method == "ldap_sync").count(),
            "sso_jit": db.query(User).filter(User.provisioning_method == "sso_jit").count(),
        }
    }
