from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.utils.database import get_db
from app.models.resource import Resource
from app.utils.websocket_manager import manager

router = APIRouter()

@router.post("/scan")
async def trigger_scan(db: AsyncSession = Depends(get_db)):
    """Trigger manual discovery scan"""
    from app.services.discovery_engine import DiscoveryEngine
    
    engine = DiscoveryEngine()
    resources = await engine.discover_all()
    
    return {
        "status": "success",
        "resources_discovered": len(resources)
    }

@router.get("/status")
async def discovery_status(db: AsyncSession = Depends(get_db)):
    """Get discovery system status"""
    result = await db.execute(select(Resource))
    total_resources = len(result.scalars().all())
    
    return {
        "status": "operational",
        "total_resources": total_resources,
        "last_scan": "2025-01-21T10:30:00Z"
    }

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo for keepalive
            await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
