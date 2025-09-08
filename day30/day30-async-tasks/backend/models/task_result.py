from sqlalchemy import Column, String, JSON, Boolean
from .base import BaseModel

class TaskResult(BaseModel):
    __tablename__ = "task_results"
    
    task_id = Column(String, unique=True, nullable=False)
    task_name = Column(String, nullable=False)
    status = Column(String, nullable=False)  # pending, running, success, failed
    result = Column(JSON)
    error_message = Column(String)
    retry_count = Column(String, default="0")
    is_chained = Column(Boolean, default=False)
    parent_task_id = Column(String)
