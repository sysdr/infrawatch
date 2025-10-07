from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from app.models.database import AlertRule, RuleTest
from app.models.rules import AlertRuleCreate, AlertRuleUpdate, BulkRuleOperation
from app.validators.rule_validator import RuleValidator
import json
from datetime import datetime

class RuleService:
    
    def __init__(self, db: Session):
        self.db = db
        self.validator = RuleValidator()
    
    def create_rule(self, rule_data: AlertRuleCreate) -> AlertRule:
        """Create a new alert rule with validation"""
        
        # Validate expression
        is_valid, message = self.validator.validate_expression(rule_data.expression)
        if not is_valid:
            raise ValueError(f"Invalid expression: {message}")
        
        # Validate thresholds
        is_valid, message = self.validator.validate_thresholds(rule_data.thresholds)
        if not is_valid:
            raise ValueError(f"Invalid thresholds: {message}")
        
        # Validate logic consistency
        is_valid, message = self.validator.validate_rule_logic(
            rule_data.expression, rule_data.thresholds
        )
        if not is_valid:
            raise ValueError(f"Logic validation failed: {message}")
        
        # Check for duplicate names
        existing = self.db.query(AlertRule).filter(AlertRule.name == rule_data.name).first()
        if existing:
            raise ValueError(f"Rule with name '{rule_data.name}' already exists")
        
        # Create rule
        db_rule = AlertRule(
            name=rule_data.name,
            description=rule_data.description,
            expression=rule_data.expression,
            severity=rule_data.severity,
            enabled=rule_data.enabled,
            template_id=rule_data.template_id,
            tags=rule_data.tags,
            thresholds=rule_data.thresholds
        )
        
        self.db.add(db_rule)
        self.db.commit()
        self.db.refresh(db_rule)
        
        return db_rule
    
    def get_rules(self, skip: int = 0, limit: int = 100, 
                  enabled_only: bool = False, tags: List[str] = None) -> List[AlertRule]:
        """Get rules with optional filtering"""
        query = self.db.query(AlertRule)
        
        if enabled_only:
            query = query.filter(AlertRule.enabled == True)
        
        if tags:
            # Filter rules that contain any of the specified tags
            for tag in tags:
                query = query.filter(AlertRule.tags.contains([tag]))
        
        return query.offset(skip).limit(limit).all()
    
    def get_rule(self, rule_id: int) -> Optional[AlertRule]:
        """Get single rule by ID"""
        return self.db.query(AlertRule).filter(AlertRule.id == rule_id).first()
    
    def update_rule(self, rule_id: int, rule_update: AlertRuleUpdate) -> AlertRule:
        """Update existing rule"""
        db_rule = self.get_rule(rule_id)
        if not db_rule:
            raise ValueError(f"Rule with ID {rule_id} not found")
        
        update_data = rule_update.dict(exclude_unset=True)
        
        # Validate if expression or thresholds are being updated
        if 'expression' in update_data or 'thresholds' in update_data:
            expression = update_data.get('expression', db_rule.expression)
            thresholds = update_data.get('thresholds', db_rule.thresholds)
            
            # Validate expression
            is_valid, message = self.validator.validate_expression(expression)
            if not is_valid:
                raise ValueError(f"Invalid expression: {message}")
            
            # Validate thresholds
            is_valid, message = self.validator.validate_thresholds(thresholds)
            if not is_valid:
                raise ValueError(f"Invalid thresholds: {message}")
            
            # Validate logic
            is_valid, message = self.validator.validate_rule_logic(expression, thresholds)
            if not is_valid:
                raise ValueError(f"Logic validation failed: {message}")
        
        # Check for name conflicts
        if 'name' in update_data:
            existing = self.db.query(AlertRule).filter(
                and_(AlertRule.name == update_data['name'], AlertRule.id != rule_id)
            ).first()
            if existing:
                raise ValueError(f"Rule with name '{update_data['name']}' already exists")
        
        # Apply updates
        for field, value in update_data.items():
            setattr(db_rule, field, value)
        
        db_rule.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_rule)
        
        return db_rule
    
    def delete_rule(self, rule_id: int) -> bool:
        """Delete rule by ID"""
        db_rule = self.get_rule(rule_id)
        if not db_rule:
            return False
        
        self.db.delete(db_rule)
        self.db.commit()
        return True
    
    def bulk_operation(self, operation: BulkRuleOperation) -> Dict[str, Any]:
        """Perform bulk operations on rules"""
        results = {
            "operation": operation.operation,
            "success_count": 0,
            "error_count": 0,
            "errors": []
        }
        
        if operation.operation == "create" and operation.rules:
            for rule_data in operation.rules:
                try:
                    self.create_rule(rule_data)
                    results["success_count"] += 1
                except Exception as e:
                    results["error_count"] += 1
                    results["errors"].append(f"Failed to create rule '{rule_data.name}': {str(e)}")
        
        elif operation.operation == "delete" and operation.rule_ids:
            for rule_id in operation.rule_ids:
                try:
                    if self.delete_rule(rule_id):
                        results["success_count"] += 1
                    else:
                        results["error_count"] += 1
                        results["errors"].append(f"Rule {rule_id} not found")
                except Exception as e:
                    results["error_count"] += 1
                    results["errors"].append(f"Failed to delete rule {rule_id}: {str(e)}")
        
        elif operation.operation in ["enable", "disable"] and operation.rule_ids:
            enabled = operation.operation == "enable"
            for rule_id in operation.rule_ids:
                try:
                    rule = self.get_rule(rule_id)
                    if rule:
                        rule.enabled = enabled
                        rule.updated_at = datetime.utcnow()
                        self.db.commit()
                        results["success_count"] += 1
                    else:
                        results["error_count"] += 1
                        results["errors"].append(f"Rule {rule_id} not found")
                except Exception as e:
                    results["error_count"] += 1
                    results["errors"].append(f"Failed to {operation.operation} rule {rule_id}: {str(e)}")
        
        return results
