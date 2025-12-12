from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models import Widget
from app.schemas import WidgetCreate, WidgetUpdate, WidgetResponse
from typing import List

router = APIRouter()

@router.post("/", response_model=WidgetResponse)
async def create_widget(widget: WidgetCreate, db: AsyncSession = Depends(get_db)):
    db_widget = Widget(**widget.model_dump())
    db.add(db_widget)
    await db.commit()
    await db.refresh(db_widget)
    return db_widget

@router.get("/dashboard/{dashboard_id}", response_model=List[WidgetResponse])
async def get_widgets(dashboard_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Widget).where(Widget.dashboard_id == dashboard_id))
    return result.scalars().all()

@router.put("/{widget_id}", response_model=WidgetResponse)
async def update_widget(widget_id: str, widget: WidgetUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Widget).where(Widget.id == widget_id))
    db_widget = result.scalar_one_or_none()
    if not db_widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    
    update_data = widget.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_widget, key, value)
    
    await db.commit()
    await db.refresh(db_widget)
    return db_widget

@router.delete("/{widget_id}")
async def delete_widget(widget_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Widget).where(Widget.id == widget_id))
    widget = result.scalar_one_or_none()
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    
    await db.delete(widget)
    await db.commit()
    return {"message": "Widget deleted successfully"}
