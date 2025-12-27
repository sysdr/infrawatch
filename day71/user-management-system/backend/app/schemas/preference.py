from pydantic import BaseModel
from typing import Dict
from datetime import datetime

class UserPreferenceUpdate(BaseModel):
    preferences: Dict

class UserPreferenceResponse(BaseModel):
    id: int
    user_id: int
    preferences: Dict
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
