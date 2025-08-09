from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import func

from ..models.server_models import Group, Server
from ..schemas.server_schemas import ServerGroupCreate, ServerGroupResponse

async def create_group(db: Session, group: ServerGroupCreate) -> ServerGroupResponse:
    """Create a new server group"""
    db_group = Group(**group.dict())
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    
    # Get server count
    server_count = db.query(func.count(Server.id)).join(Server.groups).filter(Group.id == db_group.id).scalar() or 0
    
    response = ServerGroupResponse.model_validate(db_group)
    response.server_count = server_count
    return response

async def list_groups(db: Session) -> List[ServerGroupResponse]:
    """List all server groups with server counts"""
    groups = db.query(Group).all()
    
    response_groups = []
    for group in groups:
        server_count = db.query(func.count(Server.id)).join(Server.groups).filter(Group.id == group.id).scalar() or 0
        group_response = ServerGroupResponse.model_validate(group)
        group_response.server_count = server_count
        response_groups.append(group_response)
    
    return response_groups

async def add_servers_to_group(db: Session, group_id: int, server_ids: List[int]):
    """Add servers to a group"""
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise ValueError("Group not found")
    
    servers = db.query(Server).filter(Server.id.in_(server_ids)).all()
    
    for server in servers:
        if group not in server.groups:
            server.groups.append(group)
    
    db.commit()
