from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime

class UserActivityResponse(BaseModel):
    id: int
    user_id: int
    action: str
    resource_type: Optional[str]
    resource_id: Optional[int]
    description: Optional[str]
    activity_metadata: Dict
    created_at: datetime
    
    class Config:
        from_attributes = True

class ActivityStats(BaseModel):
    total_activities: int
    activities_by_type: Dict[str, int]
    recent_activities: List[UserActivityResponse]
    activity_timeline: List[Dict]
