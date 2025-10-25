from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.template import Template, TemplateRenderRequest, TemplateRenderResponse
from app.services.template_service import TemplateService

router = APIRouter()

# Dependency to get template service
def get_template_service():
    return TemplateService()

@router.get("/", response_model=List[Template])
async def list_templates(service: TemplateService = Depends(get_template_service)):
    """List all available templates"""
    await service.initialize()
    return service.get_templates()

@router.get("/{template_id}", response_model=Template)
async def get_template(template_id: str, service: TemplateService = Depends(get_template_service)):
    """Get specific template"""
    await service.initialize()
    template = service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.post("/render", response_model=TemplateRenderResponse)
async def render_template(
    request: TemplateRenderRequest,
    service: TemplateService = Depends(get_template_service)
):
    """Render template with provided context"""
    await service.initialize()
    return await service.render_template(request)

@router.get("/{template_id}/validate")
async def validate_template(template_id: str, service: TemplateService = Depends(get_template_service)):
    """Validate template syntax and completeness"""
    await service.initialize()
    return await service.validate_template(template_id)
