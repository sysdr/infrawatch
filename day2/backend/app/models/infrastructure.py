from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class Server:
    """Represents a monitored server in our infrastructure"""
    id: str
    hostname: str
    ip_address: str
    status: str  # 'healthy', 'warning', 'critical'
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    last_heartbeat: datetime
    
    def to_dict(self) -> Dict:
        """Serialize for API responses"""
        return {
            'id': self.id,
            'hostname': self.hostname,
            'ip_address': self.ip_address,
            'status': self.status,
            'metrics': {
                'cpu_usage': self.cpu_usage,
                'memory_usage': self.memory_usage,
                'disk_usage': self.disk_usage
            },
            'last_heartbeat': self.last_heartbeat.isoformat()
        }

@dataclass
class InfrastructureCluster:
    """Represents a cluster of servers (like a Kubernetes cluster)"""
    name: str
    servers: List[Server]
    
    @property
    def healthy_servers(self) -> int:
        return len([s for s in self.servers if s.status == 'healthy'])
    
    @property
    def total_servers(self) -> int:
        return len(self.servers)
