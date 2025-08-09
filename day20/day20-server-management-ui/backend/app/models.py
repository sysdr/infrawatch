from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class ServerStatus(str, Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"

class ServerType(str, Enum):
    WEB = "web"
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"
    LOAD_BALANCER = "load_balancer"

class Server(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    hostname: str
    ip_address: str
    port: int = 22
    server_type: ServerType
    status: ServerStatus = ServerStatus.OFFLINE
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    uptime: int = 0
    tags: List[str] = []
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_checked: Optional[datetime] = None

class ServerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    hostname: str = Field(..., min_length=1)
    ip_address: str = Field(..., pattern=r'^(\d{1,3}\.){3}\d{1,3}$')
    port: int = Field(default=22, ge=1, le=65535)
    server_type: ServerType
    tags: List[str] = []
    metadata: Dict[str, Any] = {}

class ServerUpdate(BaseModel):
    name: Optional[str] = None
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    port: Optional[int] = Field(None, ge=1, le=65535)
    server_type: Optional[ServerType] = None
    status: Optional[ServerStatus] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class BulkAction(BaseModel):
    action: str  # 'delete', 'update_status', 'update_tags', 'restart'
    server_ids: List[str]
    parameters: Optional[Dict[str, Any]] = {}

class ServerListResponse(BaseModel):
    servers: List[Server]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_prev: bool

class ServerMetrics(BaseModel):
    total_servers: int
    healthy_count: int
    warning_count: int
    critical_count: int
    offline_count: int
    server_types: Dict[str, int]
