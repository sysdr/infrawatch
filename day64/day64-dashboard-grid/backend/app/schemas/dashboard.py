from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class DashboardBase(BaseModel):
    name: str
    description: Optional[str] = None
    layout: List[Dict[str, Any]] = []
    template_id: Optional[str] = None

class DashboardCreate(DashboardBase):
    pass

class DashboardUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    layout: Optional[List[Dict[str, Any]]] = None

class DashboardResponse(DashboardBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
