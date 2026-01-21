from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ContainerMetrics(BaseModel):
    """Container resource metrics"""
    container_id: str
    container_name: str
    timestamp: datetime
    
    # CPU metrics
    cpu_percent: float = Field(ge=0, le=100)
    cpu_delta: int
    system_cpu_delta: int
    
    # Memory metrics
    memory_usage: int  # bytes
    memory_limit: int  # bytes
    memory_percent: float = Field(ge=0, le=100)
    memory_cache: int  # bytes
    
    # Network metrics
    network_rx_bytes: int
    network_tx_bytes: int
    network_rx_packets: int
    network_tx_packets: int
    
    # Block I/O metrics
    blkio_read: int
    blkio_write: int
    
    # PIDs
    pids_current: Optional[int] = None


class ContainerHealth(BaseModel):
    """Container health check status"""
    container_id: str
    container_name: str
    timestamp: datetime
    
    status: str  # starting, healthy, unhealthy, none
    failing_streak: int = 0
    log: Optional[str] = None
    exit_code: Optional[int] = None


class ContainerEvent(BaseModel):
    """Container lifecycle event"""
    container_id: str
    container_name: str
    timestamp: datetime
    
    action: str  # create, start, stop, die, pause, unpause, restart, kill, remove
    status: str
    exit_code: Optional[int] = None
    error: Optional[str] = None
    
    attributes: Dict[str, Any] = Field(default_factory=dict)


class ContainerInfo(BaseModel):
    """Complete container information"""
    id: str
    name: str
    image: str
    status: str
    state: str
    created: datetime
    started_at: Optional[datetime] = None
    
    # Latest metrics
    metrics: Optional[ContainerMetrics] = None
    health: Optional[ContainerHealth] = None
    
    # Resource limits
    cpu_limit: Optional[int] = None
    memory_limit: Optional[int] = None


class MetricsQuery(BaseModel):
    """Query parameters for metrics"""
    container_ids: Optional[list[str]] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    aggregation: Optional[str] = "1m"  # 1s, 1m, 5m, 1h
    limit: int = Field(default=1000, le=10000)


class Alert(BaseModel):
    """Resource usage alert"""
    container_id: str
    container_name: str
    timestamp: datetime
    
    alert_type: str  # cpu, memory, health, restart
    severity: str  # warning, critical
    message: str
    
    current_value: float
    threshold: float
    baseline: Optional[float] = None
