from pydantic import BaseModel, validator
from typing import Dict, Any, Optional, List
from datetime import datetime

class RuleTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    template_config: Dict[str, Any]
    is_public: bool = True

    @validator('name')
    def name_must_be_valid(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Template name cannot be empty')
        return v.strip()

    @validator('category')
    def category_must_be_valid(cls, v):
        valid_categories = ['infrastructure', 'application', 'database', 'network', 'security']
        if v not in valid_categories:
            raise ValueError(f'Category must be one of: {valid_categories}')
        return v

class RuleTemplateCreate(RuleTemplateBase):
    pass

class RuleTemplateResponse(RuleTemplateBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class TemplatePreset:
    CPU_UTILIZATION = {
        "name": "CPU Utilization Alert",
        "description": "Monitors CPU usage across instances",
        "category": "infrastructure",
        "template_config": {
            "expression": "avg(cpu_usage_percent) > {threshold}",
            "thresholds": {"threshold": 85},
            "severity": "warning",
            "tags": ["infrastructure", "cpu"]
        }
    }
    
    MEMORY_UTILIZATION = {
        "name": "Memory Utilization Alert", 
        "description": "Monitors memory usage patterns",
        "category": "infrastructure",
        "template_config": {
            "expression": "avg(memory_usage_percent) > {threshold}",
            "thresholds": {"threshold": 90},
            "severity": "critical",
            "tags": ["infrastructure", "memory"]
        }
    }
    
    API_RESPONSE_TIME = {
        "name": "API Response Time Alert",
        "description": "Monitors API endpoint performance",
        "category": "application", 
        "template_config": {
            "expression": "avg(response_time_ms) > {threshold}",
            "thresholds": {"threshold": 2000},
            "severity": "warning",
            "tags": ["application", "performance"]
        }
    }
