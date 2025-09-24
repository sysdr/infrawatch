from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from ..models.alert_models import (
    AlertRule, AlertInstance, AlertState, EscalationPolicy, 
    SuppressionRule, AlertStatus, AlertSeverity, AlertOperator
)
import re

class AlertService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_alert_rule(self, rule_data: Dict[str, Any]) -> AlertRule:
        """Create a new alert rule"""
        rule = AlertRule(**rule_data)
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        return rule
    
    def list_alert_rules(self, skip: int = 0, limit: int = 100) -> List[AlertRule]:
        """List all alert rules with pagination"""
        return self.db.query(AlertRule).offset(skip).limit(limit).all()
    
    def get_alert_rule(self, rule_id: int) -> Optional[AlertRule]:
        """Get alert rule by ID"""
        return self.db.query(AlertRule).filter(AlertRule.id == rule_id).first()
    
    def update_alert_rule(self, rule_id: int, update_data: Dict[str, Any]) -> Optional[AlertRule]:
        """Update an existing alert rule"""
        rule = self.get_alert_rule(rule_id)
        if not rule:
            return None
        
        for key, value in update_data.items():
            if hasattr(rule, key):
                setattr(rule, key, value)
        
        rule.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(rule)
        return rule
    
    def delete_alert_rule(self, rule_id: int) -> bool:
        """Delete an alert rule"""
        rule = self.get_alert_rule(rule_id)
        if not rule:
            return False
        
        self.db.delete(rule)
        self.db.commit()
        return True
    
    def create_alert_instance(self, rule_id: int, current_value: float, 
                            threshold_value: float, message: str = None) -> AlertInstance:
        """Create a new alert instance when rule is triggered"""
        instance = AlertInstance(
            rule_id=rule_id,
            current_value=current_value,
            threshold_value=threshold_value,
            message=message,
            status=AlertStatus.PENDING
        )
        self.db.add(instance)
        self.db.flush()  # Flush to get the ID
        
        # Create initial state transition
        state_change = AlertState(
            alert_instance_id=instance.id,
            from_status=None,
            to_status=AlertStatus.PENDING,
            reason="Alert triggered"
        )
        self.db.add(state_change)
        
        self.db.commit()
        self.db.refresh(instance)
        return instance
    
    def update_alert_status(self, instance_id: int, new_status: AlertStatus, 
                          changed_by: str = None, reason: str = None) -> bool:
        """Update alert instance status with state tracking"""
        instance = self.db.query(AlertInstance).filter(AlertInstance.id == instance_id).first()
        if not instance:
            return False
        
        old_status = instance.status
        instance.status = new_status
        
        # Update timestamps based on status
        now = datetime.now(timezone.utc)
        if new_status == AlertStatus.ACKNOWLEDGED:
            instance.acknowledged_at = now
        elif new_status == AlertStatus.RESOLVED:
            instance.resolved_at = now
        
        # Create state transition record
        state_change = AlertState(
            alert_instance_id=instance_id,
            from_status=old_status,
            to_status=new_status,
            changed_by=changed_by,
            reason=reason
        )
        self.db.add(state_change)
        
        self.db.commit()
        return True
    
    def acknowledge_alert(self, instance_id: int, acknowledged_by: str = "system") -> bool:
        """Acknowledge an alert"""
        return self.update_alert_status(
            instance_id, 
            AlertStatus.ACKNOWLEDGED, 
            acknowledged_by, 
            "Alert acknowledged"
        )
    
    def get_active_alert_instances(self) -> List[AlertInstance]:
        """Get all currently active alert instances"""
        return self.db.query(AlertInstance).filter(
            AlertInstance.status.in_([AlertStatus.PENDING, AlertStatus.FIRING, AlertStatus.ACKNOWLEDGED])
        ).all()
    
    def create_escalation_policy(self, rule_id: int, policy_data: Dict[str, Any]) -> EscalationPolicy:
        """Create escalation policy for alert rule"""
        policy_data["alert_rule_id"] = rule_id
        policy = EscalationPolicy(**policy_data)
        self.db.add(policy)
        self.db.commit()
        self.db.refresh(policy)
        return policy
    
    def create_suppression_rule(self, rule_data: Dict[str, Any]) -> SuppressionRule:
        """Create suppression rule"""
        rule = SuppressionRule(**rule_data)
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        return rule
    
    def is_alert_suppressed(self, metric_name: str, labels: Dict[str, Any] = None) -> bool:
        """Check if an alert should be suppressed"""
        now = datetime.now(timezone.utc)
        suppression_rules = self.db.query(SuppressionRule).filter(
            SuppressionRule.is_active == True
        ).all()
        
        for rule in suppression_rules:
            # Check metric pattern match
            if re.match(rule.metric_pattern, metric_name):
                # Check time window
                if (rule.suppression_window_start and rule.suppression_window_end):
                    if rule.suppression_window_start <= now <= rule.suppression_window_end:
                        return True
                elif not rule.suppression_window_start and not rule.suppression_window_end:
                    # Always active suppression
                    return True
        
        return False
    
    def evaluate_threshold(self, rule: AlertRule, current_value: float) -> bool:
        """Evaluate if current value triggers the alert rule"""
        if rule.operator == AlertOperator.GREATER_THAN:
            return current_value > rule.threshold_value
        elif rule.operator == AlertOperator.LESS_THAN:
            return current_value < rule.threshold_value
        elif rule.operator == AlertOperator.EQUAL:
            return current_value == rule.threshold_value
        elif rule.operator == AlertOperator.NOT_EQUAL:
            return current_value != rule.threshold_value
        return False
