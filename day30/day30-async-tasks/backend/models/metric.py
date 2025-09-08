from sqlalchemy import Column, String, Float, JSON, Index
from .base import BaseModel

class Metric(BaseModel):
    __tablename__ = "metrics"
    
    name = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    source = Column(String, nullable=False)
    tags = Column(JSON, default={})
    meta_data = Column(JSON, default={})
    
    __table_args__ = (
        Index('idx_metric_name_created', 'name', 'created_at'),
        Index('idx_metric_source', 'source'),
    )
