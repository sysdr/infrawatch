from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, Boolean, Enum
from datetime import datetime
import enum
from app.core.database import Base

class SecurityCheckType(str, enum.Enum):
    INPUT_VALIDATION = "input_validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    RATE_LIMITING = "rate_limiting"
    RESOURCE_LIMITS = "resource_limits"
    CODE_INJECTION = "code_injection"

class ViolationSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SecurityCheck(Base):
    __tablename__ = "security_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(Integer, nullable=False, index=True)
    check_type = Column(Enum(SecurityCheckType), nullable=False)
    passed = Column(Boolean, default=False)
    details = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class SecurityViolation(Base):
    __tablename__ = "security_violations"
    
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(Integer, nullable=False, index=True)
    violation_type = Column(String, nullable=False)
    severity = Column(Enum(ViolationSeverity), nullable=False)
    description = Column(Text, nullable=False)
    details = Column(JSON)
    remediation = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
