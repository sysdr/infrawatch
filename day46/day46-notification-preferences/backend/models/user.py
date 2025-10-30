from sqlalchemy import Column, Integer, String, Boolean
from .base import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String, nullable=True)
    timezone = Column(String, default="UTC")
    is_active = Column(Boolean, default=True)
