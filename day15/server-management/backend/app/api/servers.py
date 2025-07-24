from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from config.database import get_db
from app.models.server import Server, Tag, HealthCheck
from app.api.schemas import (
    Server as ServerSchema, 
    ServerCreate, 
    ServerUpdate,
    Tag as TagSchema,
    TagCreate,
    HealthCheck as HealthCheckSchema,
    HealthCheckCreate
)

router = APIRouter(prefix="/api/servers", tags=["servers"])

@router.post("/", response_model=ServerSchema)
def create_server(server: ServerCreate, db: Session = Depends(get_db)):
    # Check if server with same name already exists
    existing_server = db.query(Server).filter(Server.name == server.name).first()
    if existing_server:
        raise HTTPException(
            status_code=400, 
            detail=f"Server with name '{server.name}' already exists. Please choose a different name."
        )
    
    # Create server instance
    db_server = Server(**server.dict(exclude={'tag_ids'}))
    
    # Add tags if provided
    if server.tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(server.tag_ids)).all()
        db_server.tags = tags
    
    try:
        db.add(db_server)
        db.commit()
        db.refresh(db_server)
        return db_server
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create server: {str(e)}"
        )

@router.get("/", response_model=List[ServerSchema])
def list_servers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    environment: Optional[str] = None,
    region: Optional[str] = None,
    status: Optional[str] = None,
    server_type: Optional[str] = None,
    health_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Server)
    
    if environment:
        query = query.filter(Server.environment == environment)
    if region:
        query = query.filter(Server.region == region)
    if status:
        query = query.filter(Server.status == status)
    if server_type:
        query = query.filter(Server.server_type == server_type)
    if health_status:
        query = query.filter(Server.health_status == health_status)
    
    return query.offset(skip).limit(limit).all()

@router.get("/{server_id}", response_model=ServerSchema)
def get_server(server_id: UUID, db: Session = Depends(get_db)):
    server = db.query(Server).filter(Server.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    return server

@router.put("/{server_id}", response_model=ServerSchema)
def update_server(server_id: UUID, server_update: ServerUpdate, db: Session = Depends(get_db)):
    server = db.query(Server).filter(Server.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    update_data = server_update.dict(exclude_unset=True, exclude={'tag_ids'})
    for field, value in update_data.items():
        setattr(server, field, value)
    
    # Update tags if provided
    if server_update.tag_ids is not None:
        tags = db.query(Tag).filter(Tag.id.in_(server_update.tag_ids)).all()
        server.tags = tags
    
    db.commit()
    db.refresh(server)
    return server

@router.post("/{server_id}/health", response_model=HealthCheckSchema)
def add_health_check(server_id: UUID, health_check: HealthCheckCreate, db: Session = Depends(get_db)):
    server = db.query(Server).filter(Server.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    db_health_check = HealthCheck(server_id=server_id, **health_check.dict())
    db.add(db_health_check)
    
    # Update server health status based on latest check
    if health_check.status == "critical":
        server.health_status = "failed"
    elif health_check.status == "warning":
        server.health_status = "degraded"
    else:
        server.health_status = "healthy"
    
    db.commit()
    db.refresh(db_health_check)
    return db_health_check

# Tag endpoints
@router.post("/tags/", response_model=TagSchema)
def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    db_tag = Tag(**tag.dict())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

@router.get("/tags/", response_model=List[TagSchema])
def list_tags(db: Session = Depends(get_db)):
    return db.query(Tag).all()
