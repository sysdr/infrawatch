from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.database import get_db
from app.models.rules import (
    AlertRuleCreate, AlertRuleUpdate, AlertRuleResponse, 
    BulkRuleOperation
)
from app.services.rule_service import RuleService

router = APIRouter()

@router.post("/", response_model=AlertRuleResponse)
async def create_rule(rule: AlertRuleCreate, db: Session = Depends(get_db)):
    """Create a new alert rule"""
    try:
        service = RuleService(db)
        db_rule = service.create_rule(rule)
        return db_rule
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/", response_model=List[AlertRuleResponse])
async def get_rules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    enabled_only: bool = Query(False),
    tags: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all alert rules with optional filtering"""
    service = RuleService(db)
    rules = service.get_rules(skip=skip, limit=limit, enabled_only=enabled_only, tags=tags)
    return rules

@router.get("/{rule_id}", response_model=AlertRuleResponse)
async def get_rule(rule_id: int, db: Session = Depends(get_db)):
    """Get a specific alert rule"""
    service = RuleService(db)
    rule = service.get_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule

@router.put("/{rule_id}", response_model=AlertRuleResponse)
async def update_rule(rule_id: int, rule_update: AlertRuleUpdate, db: Session = Depends(get_db)):
    """Update an existing alert rule"""
    try:
        service = RuleService(db)
        updated_rule = service.update_rule(rule_id, rule_update)
        return updated_rule
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/{rule_id}")
async def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    """Delete an alert rule"""
    service = RuleService(db)
    success = service.delete_rule(rule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"message": "Rule deleted successfully"}

@router.post("/bulk")
async def bulk_operation(operation: BulkRuleOperation, db: Session = Depends(get_db)):
    """Perform bulk operations on alert rules"""
    try:
        service = RuleService(db)
        results = service.bulk_operation(operation)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk operation failed: {str(e)}")

@router.get("/{rule_id}/validate")
async def validate_rule(rule_id: int, db: Session = Depends(get_db)):
    """Validate an existing rule"""
    service = RuleService(db)
    rule = service.get_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # Re-validate the rule
    try:
        is_valid, message = service.validator.validate_expression(rule.expression)
        if not is_valid:
            return {"valid": False, "message": message}
        
        is_valid, message = service.validator.validate_thresholds(rule.thresholds)
        if not is_valid:
            return {"valid": False, "message": message}
        
        is_valid, message = service.validator.validate_rule_logic(rule.expression, rule.thresholds)
        if not is_valid:
            return {"valid": False, "message": message}
        
        performance = service.validator.estimate_performance_impact(rule.expression)
        
        return {
            "valid": True,
            "message": "Rule is valid",
            "performance_impact": performance
        }
        
    except Exception as e:
        return {"valid": False, "message": f"Validation error: {str(e)}"}
