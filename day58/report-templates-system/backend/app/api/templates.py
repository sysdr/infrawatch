from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.template_service import TemplateService
from app.models.template import ReportFormat
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/templates", tags=["templates"])

class TemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    content: str
    format: ReportFormat = ReportFormat.HTML

class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    format: Optional[ReportFormat] = None

class PreviewRequest(BaseModel):
    data: dict

@router.post("/")
def create_template(template: TemplateCreate, db: Session = Depends(get_db)):
    """Create a new template"""
    # Validate template
    is_valid, message = TemplateService.validate_template(template.content)
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)
    
    result = TemplateService.create_template(
        db,
        name=template.name,
        description=template.description,
        content=template.content,
        format=template.format
    )
    return {
        "id": result.id,
        "name": result.name,
        "version": result.version,
        "variables": result.variables
    }

@router.get("/")
def get_templates(active_only: bool = False, db: Session = Depends(get_db)):
    """Get all templates"""
    templates = TemplateService.get_all_templates(db, active_only)
    return [
        {
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "format": t.format,
            "version": t.version,
            "variables": t.variables,
            "created_at": t.created_at.isoformat()
        }
        for t in templates
    ]

@router.get("/{template_id}")
def get_template(template_id: int, db: Session = Depends(get_db)):
    """Get template by ID"""
    template = TemplateService.get_template(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return {
        "id": template.id,
        "name": template.name,
        "description": template.description,
        "content": template.content,
        "format": template.format,
        "variables": template.variables,
        "version": template.version
    }

@router.post("/{template_id}/preview")
def preview_template(template_id: int, request: PreviewRequest, db: Session = Depends(get_db)):
    """Preview template with data"""
    template = TemplateService.get_template(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    try:
        rendered = TemplateService.render_template(template, request.data)
        return {"html": rendered}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Rendering error: {str(e)}")

@router.put("/{template_id}")
def update_template(template_id: int, updates: TemplateUpdate, db: Session = Depends(get_db)):
    """Update template"""
    update_data = updates.dict(exclude_unset=True)
    
    # Validate content if provided
    if 'content' in update_data:
        is_valid, message = TemplateService.validate_template(update_data['content'])
        if not is_valid:
            raise HTTPException(status_code=400, detail=message)
    
    template = TemplateService.update_template(db, template_id, **update_data)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return {"id": template.id, "version": template.version}

@router.delete("/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db)):
    """Delete template"""
    success = TemplateService.delete_template(db, template_id)
    if not success:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"message": "Template deleted"}
