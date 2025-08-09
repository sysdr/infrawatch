from sqlalchemy.orm import Session
from typing import List, Dict, Any
import uuid
import asyncio
import json
from datetime import datetime

from ..models.server_models import Server, BulkTask
from ..schemas.server_schemas import BulkActionRequest, BulkAction
from ..database import SessionLocal

async def execute_bulk_action(db: Session, bulk_request: BulkActionRequest) -> str:
    """Execute bulk action on multiple servers"""
    
    task_id = str(uuid.uuid4())
    
    # Create bulk task record
    bulk_task = BulkTask(
        id=task_id,
        action=bulk_request.action.value,
        server_ids=bulk_request.server_ids,
        status="pending",
        total=len(bulk_request.server_ids)
    )
    db.add(bulk_task)
    db.commit()
    
    # Process bulk action asynchronously using a new DB session inside the task
    asyncio.create_task(_process_bulk_action(task_id, bulk_request))
    
    return task_id

async def _process_bulk_action(task_id: str, bulk_request: BulkActionRequest):
    """Process bulk action in background"""
    db = SessionLocal()
    try:
        bulk_task = db.query(BulkTask).filter(BulkTask.id == task_id).first()
        bulk_task.status = "running"
        db.commit()
        
        results = []
        successful = 0
        
        for i, server_id in enumerate(bulk_request.server_ids):
            try:
                server = db.query(Server).filter(Server.id == server_id).first()
                if not server:
                    results.append({"server_id": server_id, "status": "error", "message": "Server not found"})
                    continue
                
                # Simulate action execution
                if bulk_request.action == BulkAction.START:
                    server.status = "starting"
                    await asyncio.sleep(0.1)  # Simulate processing time
                    server.status = "running"
                elif bulk_request.action == BulkAction.STOP:
                    server.status = "stopping"
                    await asyncio.sleep(0.1)
                    server.status = "stopped"
                elif bulk_request.action == BulkAction.RESTART:
                    server.status = "stopping"
                    await asyncio.sleep(0.1)
                    server.status = "starting"
                    await asyncio.sleep(0.1)
                    server.status = "running"
                elif bulk_request.action == BulkAction.UPDATE_TAGS:
                    if "tags" in bulk_request.parameters:
                        if server.tags is None:
                            server.tags = {}
                        server.tags.update(bulk_request.parameters["tags"])
                elif bulk_request.action == BulkAction.DELETE:
                    db.delete(server)
                
                server.updated_at = datetime.utcnow()
                db.commit()
                
                results.append({"server_id": server_id, "status": "success"})
                successful += 1
                
            except Exception as e:
                results.append({"server_id": server_id, "status": "error", "message": str(e)})
            
            # Update progress
            bulk_task.progress = i + 1
            db.commit()
        
        # Complete task
        bulk_task.status = "completed"
        bulk_task.result = {"results": results, "successful": successful, "failed": len(results) - successful}
        bulk_task.completed_at = datetime.utcnow()
        db.commit()
        
    except Exception as e:
        try:
            bulk_task = db.query(BulkTask).filter(BulkTask.id == task_id).first()
            if bulk_task:
                bulk_task.status = "error"
                bulk_task.error_message = str(e)
                bulk_task.completed_at = datetime.utcnow()
                db.commit()
        finally:
            pass
    finally:
        db.close()

async def get_task_status(db: Session, task_id: str) -> Dict[str, Any]:
    """Get bulk task status"""
    task = db.query(BulkTask).filter(BulkTask.id == task_id).first()
    if not task:
        return None
    
    return {
        "id": task.id,
        "action": task.action,
        "status": task.status,
        "progress": task.progress,
        "total": task.total,
        "result": task.result,
        "error_message": task.error_message,
        "created_at": task.created_at,
        "completed_at": task.completed_at
    }
