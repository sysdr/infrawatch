from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.models.database import get_db
from app.models.templates import RuleTemplateCreate, RuleTemplateResponse
from app.models.rules import AlertRuleCreate
from app.services.template_service import TemplateService
from app.services.rule_service import RuleService

router = APIRouter()

@router.post("/", response_model=RuleTemplateResponse)
async def create_template(template: RuleTemplateCreate, db: Session = Depends(get_db)):
    """Create a new rule template"""
    try:
        service = TemplateService(db)
        db_template = service.create_template(template)
        return db_template
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/", response_model=List[RuleTemplateResponse])
async def get_templates(
    category: Optional[str] = Query(None),
    public_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get all rule templates with optional filtering"""
    service = TemplateService(db)
    templates = service.get_templates(category=category, public_only=public_only)
    return templates

@router.get("/{template_id}", response_model=RuleTemplateResponse)
async def get_template(template_id: int, db: Session = Depends(get_db)):
    """Get a specific rule template"""
    service = TemplateService(db)
    template = service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.post("/{template_id}/create-rule")
async def create_rule_from_template(
    template_id: int,
    rule_name: str,
    overrides: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db)
):
    """Create a rule from template"""
    try:
        template_service = TemplateService(db)
        rule_service = RuleService(db)
        
        # Generate rule configuration from template
        rule_data = template_service.create_rule_from_template(
            template_id, rule_name, overrides
        )
        
        # Create the actual rule
        db_rule = rule_service.create_rule(rule_data)
        return db_rule
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/initialize-defaults")
async def initialize_default_templates(db: Session = Depends(get_db)):
    """Initialize system with default templates"""
    try:
        service = TemplateService(db)
        service.initialize_default_templates()
        return {"message": "Default templates initialized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize templates: {str(e)}")

@router.get("/categories/list")
async def get_template_categories():
    """Get list of available template categories"""
    return {
        "categories": [
            "infrastructure",
            "application", 
            "database",
            "network",
            "security"
        ]
    }
