from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

class LogEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: Optional[datetime] = None
    level: str = Field(..., regex="^(DEBUG|INFO|WARN|ERROR|FATAL)$")
    service: str
    message: str
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "level": "ERROR",
                "service": "auth-api",
                "message": "Authentication failed for user",
                "metadata": {"user_id": "12345", "ip": "192.168.1.1"}
            }
        }

class LogQuery(BaseModel):
    query: Optional[str] = None
    service: Optional[str] = None
    level: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: int = 100
