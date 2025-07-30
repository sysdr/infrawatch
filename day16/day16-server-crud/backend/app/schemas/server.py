from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import ipaddress

class ServerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    hostname: str = Field(..., min_length=1, max_length=255)
    ip_address: str
    server_type: Optional[str] = Field(None, max_length=50)
    environment: Optional[str] = Field(None, max_length=50)
    region: Optional[str] = Field(None, max_length=50)
    specs: Optional[Dict[str, Any]] = Field(default_factory=dict)
    server_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    tags: Optional[List[str]] = Field(default_factory=list)
    
    @validator('ip_address')
    def validate_ip_address(cls, v):
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            raise ValueError('Invalid IP address format')

class ServerCreate(ServerBase):
    tenant_id: str = Field(..., min_length=1)

class ServerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    hostname: Optional[str] = Field(None, min_length=1, max_length=255)
    ip_address: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(active|maintenance|decommissioned)$")
    server_type: Optional[str] = Field(None, max_length=50)
    environment: Optional[str] = Field(None, max_length=50)
    region: Optional[str] = Field(None, max_length=50)
    specs: Optional[Dict[str, Any]] = None
    server_metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    
    @validator('ip_address')
    def validate_ip_address(cls, v):
        if v is not None:
            try:
                ipaddress.ip_address(v)
                return v
            except ValueError:
                raise ValueError('Invalid IP address format')

class ServerResponse(ServerBase):
    id: int
    status: str
    tenant_id: str
    created_at: datetime
    updated_at: Optional[datetime]
    version: int
    
    class Config:
        from_attributes = True

class ServerList(BaseModel):
    servers: List[ServerResponse]
    total: int
    page: int
    size: int
    pages: int
