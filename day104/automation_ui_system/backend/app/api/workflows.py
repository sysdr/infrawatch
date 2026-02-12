from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.core.database import get_db
from app.services.workflow_service import WorkflowService
from app.models.workflow import WorkflowStatus

router = APIRouter()

class WorkflowCreate(BaseModel):
    name: str
    description: str
    definition: dict

class WorkflowUpdate(BaseModel):
    name: str = None
    description: str = None
    definition: dict = None
    status: WorkflowStatus = None

class WorkflowExecuteRequest(BaseModel):
    trigger_type: str = "manual"
    input_params: dict = {}

@router.post("/workflows")
def create_workflow(workflow: WorkflowCreate, db: Session = Depends(get_db)):
    return WorkflowService.create_workflow(db, workflow.name, workflow.description, workflow.definition)

@router.get("/workflows")
def list_workflows(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    workflows = WorkflowService.get_workflows(db, skip, limit)
    return {"workflows": workflows, "total": len(workflows)}

@router.get("/workflows/{workflow_id}")
def get_workflow(workflow_id: int, db: Session = Depends(get_db)):
    workflow = WorkflowService.get_workflow(db, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow

@router.put("/workflows/{workflow_id}")
def update_workflow(workflow_id: int, updates: WorkflowUpdate, db: Session = Depends(get_db)):
    update_dict = {k: v for k, v in updates.model_dump().items() if v is not None}
    workflow = WorkflowService.update_workflow(db, workflow_id, update_dict)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow

@router.delete("/workflows/{workflow_id}")
def delete_workflow(workflow_id: int, db: Session = Depends(get_db)):
    success = WorkflowService.delete_workflow(db, workflow_id)
    if not success:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"message": "Workflow deleted successfully"}

@router.post("/workflows/{workflow_id}/execute")
def execute_workflow(workflow_id: int, request: WorkflowExecuteRequest, db: Session = Depends(get_db)):
    try:
        execution = WorkflowService.execute_workflow_async(db, workflow_id, request.trigger_type, request.input_params)
        return execution
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/workflows/{workflow_id}/executions")
def list_workflow_executions(workflow_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    executions = WorkflowService.get_executions(db, workflow_id, skip, limit)
    return {"executions": executions, "total": len(executions)}

@router.get("/executions")
def list_all_executions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    executions = WorkflowService.get_executions(db, None, skip, limit)
    return {"executions": executions, "total": len(executions)}

@router.get("/executions/{execution_id}")
def get_execution(execution_id: int, db: Session = Depends(get_db)):
    execution = WorkflowService.get_execution(db, execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution

@router.get("/executions/{execution_id}/steps")
def get_execution_steps(execution_id: int, db: Session = Depends(get_db)):
    steps = WorkflowService.get_execution_steps(db, execution_id)
    return {"steps": steps, "total": len(steps)}
