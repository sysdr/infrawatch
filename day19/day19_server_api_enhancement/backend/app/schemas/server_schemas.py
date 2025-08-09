from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

class ServerStatus(str, Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    STARTING = "starting"
    STOPPING = "stopping"
    ERROR = "error"
    UNKNOWN = "unknown"

class BulkAction(str, Enum):
    START = "start"
    STOP = "stop"
    RESTART = "restart"
    DELETE = "delete"
    UPDATE_TAGS = "update_tags"

class ServerBase(BaseModel):
    name: str
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    region: Optional[str] = None
    instance_type: Optional[str] = None
    cpu_cores: Optional[int] = None
    memory_gb: Optional[int] = None
    storage_gb: Optional[int] = None
    os_type: Optional[str] = None
    tags: Dict[str, Any] = Field(default_factory=dict)

class ServerCreate(ServerBase):
    pass

class ServerResponse(ServerBase):
    id: int
    status: ServerStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class FilterCriteria(BaseModel):
    field: str
    operator: str = Field(..., pattern="^(eq|ne|in|not_in|like|gt|lt|gte|lte)$")
    value: Union[str, int, List[str], List[int]]

class SortCriteria(BaseModel):
    field: str
    direction: str = Field("asc", pattern="^(asc|desc)$")

class ServerSearchRequest(BaseModel):
    filters: List[FilterCriteria] = Field(default_factory=list)
    sort: List[SortCriteria] = Field(default_factory=list)
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    include_groups: bool = False

class ServerSearchResponse(BaseModel):
    servers: List[ServerResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class BulkActionRequest(BaseModel):
    action: BulkAction
    server_ids: List[int]
    parameters: Dict[str, Any] = Field(default_factory=dict)

class ServerGroupBase(BaseModel):
    name: str
    description: Optional[str] = None
    color: str = "#3B82F6"
    parent_id: Optional[int] = None

class ServerGroupCreate(ServerGroupBase):
    pass

class ServerGroupResponse(ServerGroupBase):
    id: int
    created_at: datetime
    server_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)

class ServerIdsRequest(BaseModel):
    server_ids: List[int]

class TemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    config: Dict[str, Any]
    version: str = "1.0.0"

class TemplateCreate(TemplateBase):
    pass

class TemplateResponse(TemplateBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TemplateDeployRequest(BaseModel):
    count: int = Field(1, ge=1, le=100)
    name_prefix: str
    override_config: Dict[str, Any] = Field(default_factory=dict)
    group_id: Optional[int] = None
