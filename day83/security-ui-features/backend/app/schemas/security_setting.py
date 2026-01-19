from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class SecuritySettingCreate(BaseModel):
    setting_key: str
    setting_name: str
    setting_value: Dict[str, Any]
    category: str
    description: Optional[str] = None
    modified_by: str

class SecuritySettingUpdate(BaseModel):
    setting_name: Optional[str] = None
    setting_value: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    modified_by: str

class SecuritySettingResponse(BaseModel):
    id: int
    setting_key: str
    setting_name: str
    setting_value: Dict[str, Any]
    category: str
    description: Optional[str]
    is_active: bool
    modified_by: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
