from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class WidgetBase(BaseModel):
    widget_type: str
    title: str
    config: Dict[str, Any] = {}
    position: Dict[str, Any] = {}

class WidgetCreate(WidgetBase):
    dashboard_id: str

class WidgetUpdate(BaseModel):
    title: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    position: Optional[Dict[str, Any]] = None

class WidgetResponse(WidgetBase):
    id: str
    dashboard_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True
