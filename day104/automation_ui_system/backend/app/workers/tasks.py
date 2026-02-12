from celery import Task
from datetime import datetime
import time
import json
from typing import Dict, Any

from app.workers.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.workflow import WorkflowExecution, ExecutionStep, ExecutionStatus
from app.core.redis_client import get_redis

class ExecutionTask(Task):
    def on_success(self, retval, task_id, args, kwargs):
        self.update_execution_status(args[0], ExecutionStatus.SUCCESS, retval)
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        self.update_execution_status(args[0], ExecutionStatus.FAILED, str(exc))
    
    def update_execution_status(self, execution_id: int, status: ExecutionStatus, result: Any):
        db = SessionLocal()
        try:
            execution = db.query(WorkflowExecution).filter(WorkflowExecution.id == execution_id).first()
            if execution:
                execution.status = status
                execution.completed_at = datetime.utcnow()
                if execution.started_at:
                    execution.duration_seconds = (execution.completed_at - execution.started_at).total_seconds()
                if status == ExecutionStatus.SUCCESS:
                    execution.output_result = result if isinstance(result, dict) else {"result": result}
                else:
                    execution.error_message = result
                db.commit()
                
                redis_client = get_redis()
                redis_client.publish(
                    "workflow_updates",
                    json.dumps({
                        "type": "execution_completed",
                        "execution_id": execution_id,
                        "status": status.value,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                )
        finally:
            db.close()

@celery_app.task(base=ExecutionTask, bind=True)
def execute_workflow(self, execution_id: int, workflow_definition: Dict):
    """Execute a workflow based on its definition"""
    db = SessionLocal()
    redis_client = get_redis()
    
    try:
        execution = db.query(WorkflowExecution).filter(WorkflowExecution.id == execution_id).first()
        if not execution:
            raise ValueError(f"Execution {execution_id} not found")
        
        execution.status = ExecutionStatus.RUNNING
        execution.started_at = datetime.utcnow()
        db.commit()
        
        redis_client.publish(
            "workflow_updates",
            json.dumps({
                "type": "execution_started",
                "execution_id": execution_id,
                "timestamp": datetime.utcnow().isoformat()
            })
        )
        
        nodes = workflow_definition.get("nodes", [])
        edges = workflow_definition.get("edges", [])
        results = {}
        
        for node in nodes:
            step_id = node["id"]
            step_type = node.get("type", "task")
            step_data = node.get("data", {})
            
            step = ExecutionStep(
                execution_id=execution_id,
                step_name=step_data.get("label", step_id),
                step_type=step_type,
                status=ExecutionStatus.RUNNING,
                started_at=datetime.utcnow(),
                input_data=step_data
            )
            db.add(step)
            db.commit()
            
            redis_client.publish(
                "workflow_updates",
                json.dumps({
                    "type": "step_started",
                    "execution_id": execution_id,
                    "step_id": step.id,
                    "step_name": step.step_name,
                    "timestamp": datetime.utcnow().isoformat()
                })
            )
            
            try:
                step_result = execute_step(step_type, step_data)
                results[step_id] = step_result
                
                step.status = ExecutionStatus.SUCCESS
                step.output_data = step_result
                step.completed_at = datetime.utcnow()
                step.duration_seconds = (step.completed_at - step.started_at).total_seconds()
                
            except Exception as e:
                step.status = ExecutionStatus.FAILED
                step.error_message = str(e)
                step.completed_at = datetime.utcnow()
                step.duration_seconds = (step.completed_at - step.started_at).total_seconds()
                db.commit()
                redis_client.publish(
                    "workflow_updates",
                    json.dumps({
                        "type": "step_failed",
                        "execution_id": execution_id,
                        "step_id": step.id,
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat()
                    })
                )
                raise
            
            db.commit()
            redis_client.publish(
                "workflow_updates",
                json.dumps({
                    "type": "step_completed",
                    "execution_id": execution_id,
                    "step_id": step.id,
                    "status": "success",
                    "timestamp": datetime.utcnow().isoformat()
                })
            )
        
        return results
        
    finally:
        db.close()

def execute_step(step_type: str, step_data: Dict) -> Dict:
    time.sleep(0.1)
    if step_type == "http_request":
        return {"status": "success", "response": "HTTP request completed"}
    elif step_type == "database_query":
        return {"status": "success", "rows": 42}
    elif step_type == "notification":
        return {"status": "success", "message": "Notification sent"}
    elif step_type == "script":
        return {"status": "success", "output": "Script executed"}
    else:
        return {"status": "success", "result": f"Executed {step_type}"}
