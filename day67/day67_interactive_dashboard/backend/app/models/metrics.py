from sqlalchemy import Column, Integer, String, Float, DateTime, Index, BigInteger
from app.core.database import Base
from datetime import datetime

class MetricData(Base):
    __tablename__ = "metric_data"
    
    id = Column(BigInteger, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    service = Column(String(100), nullable=False, index=True)
    endpoint = Column(String(200), index=True)
    region = Column(String(50), index=True)
    environment = Column(String(50), index=True)
    metric_name = Column(String(100), nullable=False, index=True)
    value = Column(Float, nullable=False)
    status = Column(String(50), index=True)
    
    __table_args__ = (
        Index('idx_timestamp_service', 'timestamp', 'service'),
        Index('idx_service_endpoint', 'service', 'endpoint'),
        Index('idx_metric_timestamp', 'metric_name', 'timestamp'),
    )
