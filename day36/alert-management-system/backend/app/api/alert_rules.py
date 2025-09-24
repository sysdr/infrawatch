from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..models.base import get_db
from ..models.alert_models import AlertRule, AlertInstance, EscalationPolicy, SuppressionRule, AlertOperator, AlertSeverity
from ..services.alert_service import AlertService
from pydantic import BaseModel

router = APIRouter(prefix="/api/alert-rules", tags=["alert-rules"])

class AlertRuleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    metric_name: str
    threshold_value: float
    operator: str
    evaluation_window: str = "5m"
    severity: str = "warning"
    labels: dict = {}

class AlertRuleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    metric_name: str
    threshold_value: float
    operator: str
    evaluation_window: str
    severity: str
    labels: dict
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.id,
            name=obj.name,
            description=obj.description,
            metric_name=obj.metric_name,
            threshold_value=obj.threshold_value,
            operator=obj.operator.value if hasattr(obj.operator, 'value') else str(obj.operator),
            evaluation_window=obj.evaluation_window,
            severity=obj.severity.value if hasattr(obj.severity, 'value') else str(obj.severity),
            labels=obj.labels,
            is_active=obj.is_active,
            created_at=obj.created_at
        )

class EscalationPolicyCreate(BaseModel):
    name: str
    alert_rule_id: int
    escalation_level: int = 1
    delay_minutes: int = 15
    notification_channels: List[str] = []
    recipients: List[str] = []

class SuppressionRuleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    metric_pattern: str
    suppression_window_start: Optional[datetime] = None
    suppression_window_end: Optional[datetime] = None
    is_maintenance_window: bool = False
    conditions: dict = {}

@router.post("/", response_model=AlertRuleResponse)
async def create_alert_rule(rule: AlertRuleCreate, db: Session = Depends(get_db)):
    alert_service = AlertService(db)
    
    # Convert string values to enum values
    rule_data = rule.dict()
    
    # Convert operator string to enum
    operator_mapping = {
        "greater_than": AlertOperator.GREATER_THAN,
        "less_than": AlertOperator.LESS_THAN,
        "equal": AlertOperator.EQUAL,
        "not_equal": AlertOperator.NOT_EQUAL,
        ">": AlertOperator.GREATER_THAN,
        "<": AlertOperator.LESS_THAN,
        "==": AlertOperator.EQUAL,
        "!=": AlertOperator.NOT_EQUAL
    }
    rule_data["operator"] = operator_mapping.get(rule_data["operator"], AlertOperator.GREATER_THAN)
    
    # Convert severity string to enum
    severity_mapping = {
        "info": AlertSeverity.INFO,
        "warning": AlertSeverity.WARNING,
        "critical": AlertSeverity.CRITICAL,
        "emergency": AlertSeverity.EMERGENCY
    }
    rule_data["severity"] = severity_mapping.get(rule_data["severity"], AlertSeverity.WARNING)
    
    created_rule = alert_service.create_alert_rule(rule_data)
    return AlertRuleResponse.from_orm(created_rule)

@router.get("/", response_model=List[AlertRuleResponse])
async def list_alert_rules(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    alert_service = AlertService(db)
    rules = alert_service.list_alert_rules(skip, limit)
    return [AlertRuleResponse.from_orm(rule) for rule in rules]

@router.get("/{rule_id}", response_model=AlertRuleResponse)
async def get_alert_rule(rule_id: int, db: Session = Depends(get_db)):
    alert_service = AlertService(db)
    rule = alert_service.get_alert_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    return AlertRuleResponse.from_orm(rule)

@router.put("/{rule_id}", response_model=AlertRuleResponse)
async def update_alert_rule(rule_id: int, rule_update: AlertRuleCreate, db: Session = Depends(get_db)):
    alert_service = AlertService(db)
    
    # Convert string values to enum values
    rule_data = rule_update.dict()
    
    # Convert operator string to enum
    operator_mapping = {
        "greater_than": AlertOperator.GREATER_THAN,
        "less_than": AlertOperator.LESS_THAN,
        "equal": AlertOperator.EQUAL,
        "not_equal": AlertOperator.NOT_EQUAL,
        ">": AlertOperator.GREATER_THAN,
        "<": AlertOperator.LESS_THAN,
        "==": AlertOperator.EQUAL,
        "!=": AlertOperator.NOT_EQUAL
    }
    rule_data["operator"] = operator_mapping.get(rule_data["operator"], AlertOperator.GREATER_THAN)
    
    # Convert severity string to enum
    severity_mapping = {
        "info": AlertSeverity.INFO,
        "warning": AlertSeverity.WARNING,
        "critical": AlertSeverity.CRITICAL,
        "emergency": AlertSeverity.EMERGENCY
    }
    rule_data["severity"] = severity_mapping.get(rule_data["severity"], AlertSeverity.WARNING)
    
    rule = alert_service.update_alert_rule(rule_id, rule_data)
    if not rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    return AlertRuleResponse.from_orm(rule)

@router.delete("/{rule_id}")
async def delete_alert_rule(rule_id: int, db: Session = Depends(get_db)):
    alert_service = AlertService(db)
    success = alert_service.delete_alert_rule(rule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    return {"message": "Alert rule deleted successfully"}

@router.post("/{rule_id}/escalation-policies")
async def create_escalation_policy(rule_id: int, policy: EscalationPolicyCreate, db: Session = Depends(get_db)):
    alert_service = AlertService(db)
    return alert_service.create_escalation_policy(rule_id, policy.dict())

@router.post("/suppression-rules")
async def create_suppression_rule(rule: SuppressionRuleCreate, db: Session = Depends(get_db)):
    alert_service = AlertService(db)
    return alert_service.create_suppression_rule(rule.dict())

@router.get("/instances/active")
async def get_active_alerts(db: Session = Depends(get_db)):
    alert_service = AlertService(db)
    return alert_service.get_active_alert_instances()

@router.post("/instances/{instance_id}/acknowledge")
async def acknowledge_alert(instance_id: int, db: Session = Depends(get_db)):
    alert_service = AlertService(db)
    return alert_service.acknowledge_alert(instance_id)
