from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, JSON, Index
from datetime import datetime
from app.core.database import Base

class Pod(Base):
    __tablename__ = "pods"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    namespace = Column(String, index=True)
    uid = Column(String, unique=True, index=True)
    status = Column(String)  # Running, Pending, Failed, Unknown
    node_name = Column(String)
    ip = Column(String, nullable=True)
    labels = Column(JSON)
    restart_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_pod_namespace_name', 'namespace', 'name'),
    )

class Service(Base):
    __tablename__ = "services"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    namespace = Column(String, index=True)
    uid = Column(String, unique=True, index=True)
    type = Column(String)  # ClusterIP, NodePort, LoadBalancer
    cluster_ip = Column(String, nullable=True)
    external_ip = Column(String, nullable=True)
    ports = Column(JSON)
    selector = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Deployment(Base):
    __tablename__ = "deployments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    namespace = Column(String, index=True)
    uid = Column(String, unique=True, index=True)
    replicas = Column(Integer)
    ready_replicas = Column(Integer, default=0)
    available_replicas = Column(Integer, default=0)
    strategy = Column(String)
    image = Column(String)
    labels = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Node(Base):
    __tablename__ = "nodes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    uid = Column(String, unique=True)
    status = Column(String)  # Ready, NotReady
    roles = Column(JSON)
    capacity_cpu = Column(Float)
    capacity_memory = Column(Float)
    allocatable_cpu = Column(Float)
    allocatable_memory = Column(Float)
    os_image = Column(String)
    kernel_version = Column(String)
    container_runtime = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ClusterHealth(Base):
    __tablename__ = "cluster_health"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    overall_score = Column(Float)
    node_health_score = Column(Float)
    pod_health_score = Column(Float)
    resource_health_score = Column(Float)
    deployment_health_score = Column(Float)
    api_latency_score = Column(Float)
    total_nodes = Column(Integer)
    ready_nodes = Column(Integer)
    total_pods = Column(Integer)
    running_pods = Column(Integer)
    failed_pods = Column(Integer)
    pending_pods = Column(Integer)

class ResourceMetrics(Base):
    __tablename__ = "resource_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    resource_type = Column(String, index=True)  # pod, node
    resource_name = Column(String, index=True)
    namespace = Column(String, index=True, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    cpu_usage = Column(Float)
    memory_usage = Column(Float)
    cpu_limit = Column(Float, nullable=True)
    memory_limit = Column(Float, nullable=True)
    
    __table_args__ = (
        Index('idx_metrics_type_name_time', 'resource_type', 'resource_name', 'timestamp'),
    )
