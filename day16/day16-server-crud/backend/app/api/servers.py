from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.crud import server_crud, audit_crud
from app.schemas import ServerCreate, ServerUpdate, ServerResponse, ServerList, AuditLogResponse

router = APIRouter(prefix="/api/servers", tags=["servers"])

# Mock authentication - replace with real auth
def get_current_user():
    return {"user_id": "admin", "tenant_id": "default"}

def get_client_ip(request: Request) -> str:
    return request.client.host

@router.post("/", response_model=ServerResponse)
def create_server(
    server: ServerCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    request: Request = None
):
    try:
        # Override tenant_id from auth
        server.tenant_id = current_user["tenant_id"]
        
        db_server = server_crud.create(
            db=db,
            obj_in=server,
            user_id=current_user["user_id"]
        )
        return db_server
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=ServerList)
def list_servers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    environment: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    result = server_crud.get_multi(
        db=db,
        tenant_id=current_user["tenant_id"],
        skip=skip,
        limit=limit,
        status=status,
        environment=environment,
        region=region,
        search=search
    )
    return result

@router.get("/{server_id}", response_model=ServerResponse)
def get_server(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    server = server_crud.get(
        db=db,
        id=server_id,
        tenant_id=current_user["tenant_id"]
    )
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    return server

@router.put("/{server_id}", response_model=ServerResponse)
def update_server(
    server_id: int,
    server_update: ServerUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    server = server_crud.get(
        db=db,
        id=server_id,
        tenant_id=current_user["tenant_id"]
    )
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    updated_server = server_crud.update(
        db=db,
        db_obj=server,
        obj_in=server_update,
        user_id=current_user["user_id"]
    )
    return updated_server

@router.delete("/{server_id}", response_model=ServerResponse)
def delete_server(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    server = server_crud.get(
        db=db,
        id=server_id,
        tenant_id=current_user["tenant_id"]
    )
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    deleted_server = server_crud.soft_delete(
        db=db,
        db_obj=server,
        user_id=current_user["user_id"]
    )
    return deleted_server

@router.get("/{server_id}/audit", response_model=list[AuditLogResponse])
def get_server_audit_logs(
    server_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Verify server exists and belongs to tenant
    server = server_crud.get(
        db=db,
        id=server_id,
        tenant_id=current_user["tenant_id"]
    )
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    logs = audit_crud.get_logs(
        db=db,
        tenant_id=current_user["tenant_id"],
        resource_id=str(server_id),
        skip=skip,
        limit=limit
    )
    return logs
