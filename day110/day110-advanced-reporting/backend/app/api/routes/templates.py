from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db, ReportTemplate
from app.api.schemas.report_schemas import TemplateCreate, TemplateResponse
from typing import List

router = APIRouter()

@router.post("/", response_model=TemplateResponse)
def create_template(template: TemplateCreate, db: Session = Depends(get_db)):
    """Create a new report template"""
    
    # Check for duplicate name
    existing = db.query(ReportTemplate).filter(ReportTemplate.name == template.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Template name already exists")
    
    db_template = ReportTemplate(
        name=template.name,
        description=template.description,
        query_config=template.query_config,
        layout_config=template.layout_config,
        parent_template_id=template.parent_template_id,
        version=1
    )
    
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    
    return db_template

@router.get("/", response_model=List[TemplateResponse])
def list_templates(db: Session = Depends(get_db)):
    """List all templates"""
    templates = db.query(ReportTemplate).filter(ReportTemplate.is_active == True).all()
    return templates

@router.get("/{template_id}", response_model=TemplateResponse)
def get_template(template_id: int, db: Session = Depends(get_db)):
    """Get specific template"""
    template = db.query(ReportTemplate).filter(ReportTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.put("/{template_id}", response_model=TemplateResponse)
def update_template(template_id: int, template: TemplateCreate, db: Session = Depends(get_db)):
    """Update template (creates new version)"""
    
    existing = db.query(ReportTemplate).filter(ReportTemplate.id == template_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Create new version
    new_template = ReportTemplate(
        name=existing.name,
        description=template.description,
        query_config=template.query_config,
        layout_config=template.layout_config,
        parent_template_id=template_id,
        version=existing.version + 1
    )
    
    db.add(new_template)
    db.commit()
    db.refresh(new_template)
    
    return new_template
