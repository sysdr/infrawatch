from fastapi import FastAPI, HTTPException, Depends, Query, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json
import io
import pandas as pd
from datetime import datetime

from .database import get_db, engine, Base
from .models import server_models
from .services import filter_service, bulk_service, group_service, template_service, export_service
from .schemas import server_schemas

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Server API Enhancement",
    description="Advanced server management with filtering, bulk ops, and templates",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Server API Enhancement - Day 19"}

# Advanced filtering endpoint
@app.post("/api/servers/search", response_model=server_schemas.ServerSearchResponse)
async def search_servers(
    search_request: server_schemas.ServerSearchRequest,
    db: Session = Depends(get_db)
):
    """Advanced server search with multiple filters"""
    try:
        result = await filter_service.search_servers(db, search_request)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Bulk operations
@app.post("/api/servers/bulk-action")
async def bulk_action(
    bulk_request: server_schemas.BulkActionRequest,
    db: Session = Depends(get_db)
):
    """Perform bulk operations on multiple servers"""
    try:
        task_id = await bulk_service.execute_bulk_action(db, bulk_request)
        return {"task_id": task_id, "status": "started"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/bulk-tasks/{task_id}")
async def get_bulk_task_status(task_id: str, db: Session = Depends(get_db)):
    """Get bulk operation status"""
    status = await bulk_service.get_task_status(db, task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    return status

# Server groups
@app.post("/api/server-groups", response_model=server_schemas.ServerGroupResponse)
async def create_server_group(
    group: server_schemas.ServerGroupCreate,
    db: Session = Depends(get_db)
):
    """Create a new server group"""
    return await group_service.create_group(db, group)

@app.get("/api/server-groups", response_model=List[server_schemas.ServerGroupResponse])
async def list_server_groups(db: Session = Depends(get_db)):
    """List all server groups"""
    return await group_service.list_groups(db)

@app.post("/api/server-groups/{group_id}/servers")
async def add_servers_to_group(
    group_id: int,
    server_ids: server_schemas.ServerIdsRequest,
    db: Session = Depends(get_db)
):
    """Add servers to a group"""
    await group_service.add_servers_to_group(db, group_id, server_ids.server_ids)
    return {"message": "Servers added to group successfully"}

# Templates
@app.post("/api/templates", response_model=server_schemas.TemplateResponse)
async def create_template(
    template: server_schemas.TemplateCreate,
    db: Session = Depends(get_db)
):
    """Create a server template"""
    return await template_service.create_template(db, template)

@app.get("/api/templates", response_model=List[server_schemas.TemplateResponse])
async def list_templates(db: Session = Depends(get_db)):
    """List all templates"""
    return await template_service.list_templates(db)

@app.post("/api/templates/{template_id}/deploy")
async def deploy_from_template(
    template_id: int,
    deploy_request: server_schemas.TemplateDeployRequest,
    db: Session = Depends(get_db)
):
    """Deploy servers from template"""
    result = await template_service.deploy_from_template(db, template_id, deploy_request)
    return result

# Import/Export
@app.post("/api/servers/import")
async def import_servers(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Import servers from CSV/Excel file"""
    try:
        result = await export_service.import_servers(db, file)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/servers/export")
async def export_servers(
    format: str = Query("csv", pattern="^(csv|excel)$"),
    group_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Export servers to CSV or Excel"""
    try:
        file_content, filename, media_type = await export_service.export_servers(
            db, format, group_id
        )
        return StreamingResponse(
            io.BytesIO(file_content),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
