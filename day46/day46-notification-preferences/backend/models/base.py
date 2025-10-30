from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TimestampMixin:
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class BaseModel(Base, TimestampMixin):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
