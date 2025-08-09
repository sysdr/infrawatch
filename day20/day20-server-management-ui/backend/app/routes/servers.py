from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import List, Optional
import asyncio

from ..models import Server, ServerCreate, ServerUpdate, BulkAction, ServerListResponse, ServerStatus, ServerMetrics
from ..services import ServerService

router = APIRouter()
server_service = ServerService()

@router.get("/", response_model=ServerListResponse)
async def get_servers(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[ServerStatus] = None,
    server_type: Optional[str] = None
):
    """Get paginated server list with filtering"""
    servers = await server_service.get_all_servers(page, page_size, search, status, server_type)
    total_servers = len(list(server_service.servers.values()))
    
    return ServerListResponse(
        servers=servers,
        total=total_servers,
        page=page,
        page_size=page_size,
        has_next=(page * page_size) < total_servers,
        has_prev=page > 1
    )

@router.get("/metrics", response_model=ServerMetrics)
async def get_server_metrics():
    """Get server metrics summary"""
    return await server_service.get_metrics()

@router.get("/{server_id}", response_model=Server)
async def get_server(server_id: str):
    """Get specific server details"""
    server = await server_service.get_server(server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    return server

@router.post("/", response_model=Server)
async def create_server(server_data: ServerCreate, background_tasks: BackgroundTasks):
    """Create new server"""
    server = await server_service.create_server(server_data)
    
    # Start background status check
    background_tasks.add_task(check_server_health, server.id)
    
    return server

@router.put("/{server_id}", response_model=Server)
async def update_server(server_id: str, server_data: ServerUpdate):
    """Update existing server"""
    server = await server_service.update_server(server_id, server_data)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    return server

@router.delete("/{server_id}")
async def delete_server(server_id: str):
    """Delete server"""
    success = await server_service.delete_server(server_id)
    if not success:
        raise HTTPException(status_code=404, detail="Server not found")
    return {"message": "Server deleted successfully"}

@router.post("/bulk-action")
async def bulk_server_action(bulk_action: BulkAction, background_tasks: BackgroundTasks):
    """Execute bulk action on multiple servers"""
    results = await server_service.bulk_action(bulk_action)
    
    # Add background task for post-action processing
    background_tasks.add_task(post_bulk_action_processing, bulk_action, results)
    
    return results

@router.post("/{server_id}/check-status")
async def check_server_status(server_id: str):
    """Manually trigger server status check"""
    status = await server_service.check_server_status(server_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Server not found")
    
    return {"server_id": server_id, "status": status}

async def check_server_health(server_id: str):
    """Background task to check server health"""
    await asyncio.sleep(5)  # Simulate connection delay
    await server_service.check_server_status(server_id)

async def post_bulk_action_processing(bulk_action: BulkAction, results: dict):
    """Background processing after bulk actions"""
    await asyncio.sleep(1)
    # Could send notifications, update logs, etc.
    print(f"Bulk action {bulk_action.action} completed: {len(results['success'])} success, {len(results['failed'])} failed")
