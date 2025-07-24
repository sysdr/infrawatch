from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class TagBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: str = "custom"
    color: str = "#3B82F6"

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class HealthCheckBase(BaseModel):
    cpu_usage: Optional[int] = Field(None, ge=0, le=100)
    memory_usage: Optional[int] = Field(None, ge=0, le=100)
    disk_usage: Optional[int] = Field(None, ge=0, le=100)
    network_latency: Optional[int] = Field(None, ge=0)
    service_status: Optional[Dict[str, Any]] = None
    error_count: int = 0
    warning_count: int = 0
    check_type: str = "automated"
    status: str = "healthy"
    message: Optional[str] = None

class HealthCheckCreate(HealthCheckBase):
    pass

class HealthCheck(HealthCheckBase):
    id: int
    server_id: UUID
    checked_at: datetime
    
    class Config:
        from_attributes = True

class ServerBase(BaseModel):
    name: str
    hostname: str
    ip_address: str
    port: int = 22
    cpu_cores: Optional[int] = None
    memory_gb: Optional[int] = None
    storage_gb: Optional[int] = None
    os_type: Optional[str] = None
    os_version: Optional[str] = None
    environment: Optional[str] = None
    region: Optional[str] = None
    availability_zone: Optional[str] = None
    server_type: Optional[str] = None
    server_metadata: Optional[Dict[str, Any]] = None
    configuration: Optional[Dict[str, Any]] = None

class ServerCreate(ServerBase):
    tag_ids: Optional[List[int]] = []

class ServerUpdate(BaseModel):
    name: Optional[str] = None
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    port: Optional[int] = None
    cpu_cores: Optional[int] = None
    memory_gb: Optional[int] = None
    storage_gb: Optional[int] = None
    os_type: Optional[str] = None
    os_version: Optional[str] = None
    status: Optional[str] = None
    health_status: Optional[str] = None
    environment: Optional[str] = None
    region: Optional[str] = None
    availability_zone: Optional[str] = None
    server_type: Optional[str] = None
    server_metadata: Optional[Dict[str, Any]] = None
    configuration: Optional[Dict[str, Any]] = None
    tag_ids: Optional[List[int]] = None

class Server(ServerBase):
    id: UUID
    status: str
    health_status: str
    last_heartbeat: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[str]
    tags: List[Tag] = []
    health_checks: List[HealthCheck] = []
    
    class Config:
        from_attributes = True
