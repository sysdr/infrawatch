from pydantic import BaseModel, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class SeverityLevel(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning" 
    INFO = "info"

class RuleStatus(str, Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    TESTING = "testing"

class AlertRuleBase(BaseModel):
    name: str
    description: Optional[str] = None
    expression: str
    severity: SeverityLevel = SeverityLevel.WARNING
    enabled: bool = True
    tags: List[str] = []
    thresholds: Dict[str, Any]

    @validator('name')
    def name_must_be_valid(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Name cannot be empty')
        if len(v) > 255:
            raise ValueError('Name too long')
        return v.strip()

    @validator('expression')
    def expression_must_be_valid(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Expression cannot be empty')
        return v.strip()

class AlertRuleCreate(AlertRuleBase):
    template_id: Optional[int] = None

class AlertRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    expression: Optional[str] = None
    severity: Optional[SeverityLevel] = None
    enabled: Optional[bool] = None
    tags: Optional[List[str]] = None
    thresholds: Optional[Dict[str, Any]] = None

class AlertRuleResponse(AlertRuleBase):
    id: int
    template_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    created_by: str

    class Config:
        from_attributes = True

class BulkRuleOperation(BaseModel):
    operation: str  # create, update, delete, enable, disable
    rule_ids: Optional[List[int]] = None
    rules: Optional[List[AlertRuleCreate]] = None
    updates: Optional[AlertRuleUpdate] = None

class RuleTestRequest(BaseModel):
    rule_id: Optional[int] = None
    rule_config: Optional[AlertRuleCreate] = None
    test_data: List[Dict[str, Any]]
    expected_results: List[bool]

class RuleTestResponse(BaseModel):
    test_id: int
    rule_id: int
    passed: bool
    results: List[Dict[str, Any]]
    execution_time_ms: float
