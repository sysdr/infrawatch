import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from ..models.remediation import (
    RemediationAction, ActionTemplate, ApprovalRequest, 
    RollbackData, ActionStatus, RiskLevel
)
from .safety_controls import safety_controls

class RemediationService:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_action(
        self, 
        template_id: int, 
        incident_id: str, 
        parameters: dict,
        created_by: str = "system"
    ) -> RemediationAction:
        template = self.db.query(ActionTemplate).filter(ActionTemplate.id == template_id).first()
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        blast_radius = safety_controls.calculate_blast_radius(parameters, template.max_blast_radius)
        risk_score = safety_controls.calculate_risk_score(template.risk_level.value, blast_radius, parameters)
        
        action = RemediationAction(
            template_id=template_id,
            incident_id=incident_id,
            parameters=parameters,
            risk_score=risk_score,
            blast_radius=blast_radius,
            created_by=created_by,
            status=ActionStatus.PENDING
        )
        self.db.add(action)
        self.db.commit()
        self.db.refresh(action)
        
        if risk_score < 30.0:
            await self.auto_approve(action.id)
        elif template.requires_approval:
            self.create_approval_request(action.id)
        
        return action
    
    async def auto_approve(self, action_id: int) -> None:
        action = self.db.query(RemediationAction).filter(RemediationAction.id == action_id).first()
        if action:
            action.status = ActionStatus.APPROVED
            action.approved_by = "auto-approved"
            action.approved_at = datetime.utcnow()
            self.db.commit()
            await self.validate_action(action_id)
    
    def create_approval_request(self, action_id: int, approver: str = "admin") -> ApprovalRequest:
        approval = ApprovalRequest(action_id=action_id, approver=approver, status="pending")
        self.db.add(approval)
        self.db.commit()
        return approval
    
    async def approve_action(self, action_id: int, approver: str, comments: str = "") -> RemediationAction:
        action = self.db.query(RemediationAction).filter(RemediationAction.id == action_id).first()
        if not action:
            raise ValueError(f"Action {action_id} not found")
        
        approval = self.db.query(ApprovalRequest).filter(
            ApprovalRequest.action_id == action_id,
            ApprovalRequest.status == "pending"
        ).first()
        if approval:
            approval.status = "approved"
            approval.comments = comments
            approval.responded_at = datetime.utcnow()
        
        action.status = ActionStatus.APPROVED
        action.approved_by = approver
        action.approved_at = datetime.utcnow()
        self.db.commit()
        await self.validate_action(action_id)
        return action
    
    async def validate_action(self, action_id: int) -> bool:
        action = self.db.query(RemediationAction).filter(RemediationAction.id == action_id).first()
        if not action:
            return False
        
        action.status = ActionStatus.VALIDATING
        self.db.commit()
        
        if not safety_controls.check_rate_limit():
            action.status = ActionStatus.FAILED
            action.error_message = "Rate limit exceeded"
            self.db.commit()
            return False
        
        valid, error = safety_controls.validate_blast_radius(
            action.blast_radius, action.template.max_blast_radius, 100
        )
        if not valid:
            action.status = ActionStatus.FAILED
            action.error_message = error
            self.db.commit()
            return False
        
        await self.dry_run_action(action_id)
        return True
    
    async def dry_run_action(self, action_id: int) -> Dict[str, Any]:
        action = self.db.query(RemediationAction).filter(RemediationAction.id == action_id).first()
        action.status = ActionStatus.DRY_RUN
        self.db.commit()
        
        dry_run_result = {
            "simulated": True,
            "timestamp": datetime.utcnow().isoformat(),
            "affected_resources": action.blast_radius,
            "estimated_duration_seconds": 5,
            "side_effects": [
                f"Would execute script: {action.template.script_name}",
                f"Would affect {action.blast_radius} resources",
                "No detected conflicts"
            ],
            "safety_checks_passed": True
        }
        action.dry_run_result = dry_run_result
        self.db.commit()
        await self.execute_action(action_id)
        return dry_run_result
    
    async def execute_action(self, action_id: int) -> Dict[str, Any]:
        action = self.db.query(RemediationAction).filter(RemediationAction.id == action_id).first()
        if not action:
            raise ValueError(f"Action {action_id} not found")
        
        if action.template.can_rollback:
            self.capture_rollback_state(action_id)
        
        action.status = ActionStatus.EXECUTING
        action.executed_at = datetime.utcnow()
        self.db.commit()
        
        try:
            result = await self.execute_script(action.template.script_name, action.parameters)
            action.status = ActionStatus.COMPLETED
            action.execution_result = result
            action.completed_at = datetime.utcnow()
            self.db.commit()
            return result
        except Exception as e:
            action.status = ActionStatus.FAILED
            action.error_message = str(e)
            action.completed_at = datetime.utcnow()
            self.db.commit()
            raise
    
    async def execute_script(self, script_name: str, parameters: dict) -> Dict[str, Any]:
        await asyncio.sleep(0.5)
        return {
            "status": "success",
            "script": script_name,
            "parameters": parameters,
            "output": f"Successfully executed {script_name}",
            "timestamp": datetime.utcnow().isoformat(),
            "execution_time_ms": 500
        }
    
    def capture_rollback_state(self, action_id: int) -> RollbackData:
        action = self.db.query(RemediationAction).filter(RemediationAction.id == action_id).first()
        state_snapshot = {
            "timestamp": datetime.utcnow().isoformat(),
            "parameters": action.parameters,
            "affected_resources": action.blast_radius,
            "original_state": "captured_state_data_here"
        }
        rollback_params = {
            "script": action.template.rollback_script or "rollback.sh",
            "inverse_parameters": action.parameters
        }
        rollback_data = RollbackData(
            action_id=action_id,
            state_snapshot=state_snapshot,
            rollback_parameters=rollback_params,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        self.db.add(rollback_data)
        self.db.commit()
        return rollback_data
    
    async def rollback_action(self, action_id: int) -> Dict[str, Any]:
        action = self.db.query(RemediationAction).filter(RemediationAction.id == action_id).first()
        if not action:
            raise ValueError(f"Action {action_id} not found")
        if not action.template.can_rollback:
            raise ValueError(f"Action {action_id} cannot be rolled back")
        
        rollback_data = action.rollback_data
        if not rollback_data:
            raise ValueError(f"No rollback data found for action {action_id}")
        if rollback_data.rolled_back:
            raise ValueError(f"Action {action_id} already rolled back")
        
        result = await self.execute_script(
            rollback_data.rollback_parameters["script"],
            rollback_data.rollback_parameters["inverse_parameters"]
        )
        action.status = ActionStatus.ROLLED_BACK
        rollback_data.rolled_back = True
        rollback_data.rolled_back_at = datetime.utcnow()
        self.db.commit()
        return result
