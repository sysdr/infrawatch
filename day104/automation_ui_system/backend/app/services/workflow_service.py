from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime

from app.models.workflow import (
    Workflow, WorkflowExecution, ExecutionStep, AutomationScript,
    WorkflowStatus, ExecutionStatus
)
from app.workers.tasks import execute_workflow

class WorkflowService:
    @staticmethod
    def create_workflow(db: Session, name: str, description: str, definition: Dict) -> Workflow:
        workflow = Workflow(
            name=name,
            description=description,
            definition=definition,
            status=WorkflowStatus.DRAFT
        )
        db.add(workflow)
        db.commit()
        db.refresh(workflow)
        return workflow
    
    @staticmethod
    def get_workflows(db: Session, skip: int = 0, limit: int = 100) -> List[Workflow]:
        return db.query(Workflow).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_workflow(db: Session, workflow_id: int) -> Optional[Workflow]:
        return db.query(Workflow).filter(Workflow.id == workflow_id).first()
    
    @staticmethod
    def update_workflow(db: Session, workflow_id: int, updates: Dict) -> Optional[Workflow]:
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            return None
        for key, value in updates.items():
            setattr(workflow, key, value)
        workflow.version += 1
        workflow.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(workflow)
        return workflow
    
    @staticmethod
    def delete_workflow(db: Session, workflow_id: int) -> bool:
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            return False
        db.delete(workflow)
        db.commit()
        return True
    
    @staticmethod
    def execute_workflow_async(db: Session, workflow_id: int, trigger_type: str, input_params: Dict = None) -> WorkflowExecution:
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            status=ExecutionStatus.QUEUED,
            trigger_type=trigger_type,
            input_params=input_params or {}
        )
        db.add(execution)
        db.commit()
        db.refresh(execution)
        execute_workflow.delay(execution.id, workflow.definition)
        return execution
    
    @staticmethod
    def get_executions(db: Session, workflow_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[WorkflowExecution]:
        query = db.query(WorkflowExecution)
        if workflow_id:
            query = query.filter(WorkflowExecution.workflow_id == workflow_id)
        return query.order_by(WorkflowExecution.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_execution(db: Session, execution_id: int) -> Optional[WorkflowExecution]:
        return db.query(WorkflowExecution).filter(WorkflowExecution.id == execution_id).first()
    
    @staticmethod
    def get_execution_steps(db: Session, execution_id: int) -> List[ExecutionStep]:
        return db.query(ExecutionStep).filter(ExecutionStep.execution_id == execution_id).all()

class ScriptService:
    @staticmethod
    def create_script(db: Session, name: str, description: str, script_type: str, content: str, workflow_id: Optional[int] = None) -> AutomationScript:
        script = AutomationScript(
            name=name,
            description=description,
            script_type=script_type,
            content=content,
            workflow_id=workflow_id
        )
        db.add(script)
        db.commit()
        db.refresh(script)
        return script
    
    @staticmethod
    def get_scripts(db: Session, skip: int = 0, limit: int = 100) -> List[AutomationScript]:
        return db.query(AutomationScript).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_script(db: Session, script_id: int) -> Optional[AutomationScript]:
        return db.query(AutomationScript).filter(AutomationScript.id == script_id).first()
    
    @staticmethod
    def update_script(db: Session, script_id: int, updates: Dict) -> Optional[AutomationScript]:
        script = db.query(AutomationScript).filter(AutomationScript.id == script_id).first()
        if not script:
            return None
        for key, value in updates.items():
            setattr(script, key, value)
        script.version += 1
        script.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(script)
        return script
    
    @staticmethod
    def delete_script(db: Session, script_id: int) -> bool:
        script = db.query(AutomationScript).filter(AutomationScript.id == script_id).first()
        if not script:
            return False
        db.delete(script)
        db.commit()
        return True
