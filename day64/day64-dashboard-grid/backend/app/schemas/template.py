from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class TemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    layout: List[Dict[str, Any]] = []
    widget_configs: List[Dict[str, Any]] = []
    is_public: bool = True

class TemplateCreate(TemplateBase):
    pass

class TemplateResponse(TemplateBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True
