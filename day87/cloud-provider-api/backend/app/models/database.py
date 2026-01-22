from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Enum
from datetime import datetime
import enum

from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class ResourceType(enum.Enum):
    EC2 = "ec2"
    RDS = "rds"
    S3 = "s3"
    LAMBDA = "lambda"
    ECS = "ecs"

class HealthStatus(enum.Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    FAILED = "failed"

class Resource(Base):
    __tablename__ = "resources"
    
    id = Column(Integer, primary_key=True)
    resource_id = Column(String, unique=True, index=True)
    resource_type = Column(Enum(ResourceType))
    region = Column(String, index=True)
    name = Column(String)
    state = Column(String)
    resource_metadata = Column(JSON, name='metadata')  # Use name parameter to keep DB column name
    tags = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CostRecord(Base):
    __tablename__ = "cost_records"
    
    id = Column(Integer, primary_key=True)
    resource_id = Column(String, index=True)
    resource_type = Column(String)
    region = Column(String)
    cost_usd = Column(Float)
    usage_hours = Column(Float)
    pricing_model = Column(String)  # on-demand, reserved, spot
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    metadata = Column(JSON)

class HealthMetric(Base):
    __tablename__ = "health_metrics"
    
    id = Column(Integer, primary_key=True)
    resource_id = Column(String, index=True)
    resource_type = Column(String)
    health_status = Column(Enum(HealthStatus))
    health_score = Column(Integer)  # 0-100
    availability = Column(Float)  # 0-1
    latency_p95 = Column(Float)
    error_rate = Column(Float)
    cpu_utilization = Column(Float)
    memory_utilization = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class AutoScalingEvent(Base):
    __tablename__ = "autoscaling_events"
    
    id = Column(Integer, primary_key=True)
    group_name = Column(String, index=True)
    region = Column(String)
    event_type = Column(String)  # scale_up, scale_down
    trigger_metric = Column(String)
    trigger_value = Column(Float)
    old_capacity = Column(Integer)
    new_capacity = Column(Integer)
    cost_impact = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    metadata = Column(JSON)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
