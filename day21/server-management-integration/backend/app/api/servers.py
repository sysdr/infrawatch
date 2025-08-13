from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.models.server import Server, ServerStatus
from app.services.server_service import ServerService
from app.websocket.manager import ConnectionManager
from pydantic import BaseModel

router = APIRouter(prefix="/servers", tags=["servers"])

# Global connection manager instance
manager = ConnectionManager()
server_service = ServerService(manager)

class ServerCreate(BaseModel):
    name: str
    description: str = None
    ip_address: str = None
    port: int = None

class ServerUpdate(BaseModel):
    name: str = None
    description: str = None
    status: ServerStatus = None

@router.post("/", response_model=dict)
async def create_server(server_data: ServerCreate, db: AsyncSession = Depends(get_db)):
    try:
        server = await server_service.create_server(db, server_data.model_dump())
        return {"success": True, "data": server.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=dict)
async def list_servers(db: AsyncSession = Depends(get_db)):
    servers = await server_service.get_servers(db)
    return {"success": True, "data": [server.to_dict() for server in servers]}

@router.get("/{server_id}", response_model=dict)
async def get_server(server_id: int, db: AsyncSession = Depends(get_db)):
    server = await server_service.get_server(db, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    return {"success": True, "data": server.to_dict()}

@router.put("/{server_id}/status", response_model=dict)
async def update_server_status(server_id: int, status: ServerStatus, db: AsyncSession = Depends(get_db)):
    try:
        server = await server_service.update_server_status(db, server_id, status)
        if not server:
            raise HTTPException(status_code=404, detail="Server not found")
        return {"success": True, "data": server.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{server_id}", response_model=dict)
async def delete_server(server_id: int, db: AsyncSession = Depends(get_db)):
    success = await server_service.delete_server(db, server_id)
    if not success:
        raise HTTPException(status_code=404, detail="Server not found")
    return {"success": True, "message": "Server deleted successfully"}
