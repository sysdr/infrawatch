from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models import Template, Dashboard, Widget
from app.schemas import TemplateCreate, TemplateResponse
from typing import List

router = APIRouter()

@router.post("/", response_model=TemplateResponse)
async def create_template(template: TemplateCreate, db: AsyncSession = Depends(get_db)):
    db_template = Template(**template.model_dump())
    db.add(db_template)
    await db.commit()
    await db.refresh(db_template)
    return db_template

@router.get("/", response_model=List[TemplateResponse])
async def get_templates(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Template).where(Template.is_public == 1))
    return result.scalars().all()

@router.post("/{template_id}/apply/{dashboard_id}")
async def apply_template(template_id: str, dashboard_id: str, db: AsyncSession = Depends(get_db)):
    # Get template
    result = await db.execute(select(Template).where(Template.id == template_id))
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Get dashboard
    result = await db.execute(select(Dashboard).where(Dashboard.id == dashboard_id))
    dashboard = result.scalar_one_or_none()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    # Delete existing widgets
    result = await db.execute(select(Widget).where(Widget.dashboard_id == dashboard_id))
    existing_widgets = result.scalars().all()
    for widget in existing_widgets:
        await db.delete(widget)
    
    # Apply template layout and widgets
    dashboard.layout = template.layout
    dashboard.template_id = template_id
    
    for widget_config in template.widget_configs:
        widget = Widget(
            dashboard_id=dashboard_id,
            widget_type=widget_config['widget_type'],
            title=widget_config['title'],
            config=widget_config.get('config', {}),
            position=widget_config.get('position', {})
        )
        db.add(widget)
    
    await db.commit()
    return {"message": "Template applied successfully"}
