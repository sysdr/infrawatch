from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Float, ForeignKey, Text
from sqlalchemy.sql import func
from app.core.database import Base

class SecurityEvent(Base):
    __tablename__ = "security_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100), index=True)
    severity = Column(String(20), index=True)
    source_ip = Column(String(45), index=True)
    user_id = Column(Integer, nullable=True, index=True)
    endpoint = Column(String(255))
    request_data = Column(JSON)
    detected_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    response_status = Column(String(50))
    threat_score = Column(Float, default=0.0)
    event_metadata = Column(JSON)
    correlation_id = Column(String(100), index=True)

class ThreatPattern(Base):
    __tablename__ = "threat_patterns"
    
    id = Column(Integer, primary_key=True, index=True)
    pattern_name = Column(String(100), unique=True)
    pattern_type = Column(String(50))
    pattern_data = Column(JSON)
    severity = Column(String(20))
    enabled = Column(Boolean, default=True)
    detection_count = Column(Integer, default=0)
    last_detected = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class IncidentResponse(Base):
    __tablename__ = "incident_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String(100), unique=True, index=True)
    severity = Column(String(20))
    status = Column(String(50))
    event_count = Column(Integer, default=1)
    first_detected = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    affected_systems = Column(JSON)
    response_actions = Column(JSON)
    assigned_to = Column(String(100))
    notes = Column(Text)
    auto_response = Column(Boolean, default=False)

class SecurityTest(Base):
    __tablename__ = "security_tests"
    
    id = Column(Integer, primary_key=True, index=True)
    test_name = Column(String(200))
    test_type = Column(String(50))
    test_suite = Column(String(100))
    status = Column(String(20))
    duration_ms = Column(Integer)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    results = Column(JSON)
    failure_reason = Column(Text, nullable=True)

class SecurityAssessment(Base):
    __tablename__ = "security_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(String(100), unique=True, index=True)
    assessment_type = Column(String(50))
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20))
    findings = Column(JSON)
    score = Column(Float)
    passed_checks = Column(Integer, default=0)
    failed_checks = Column(Integer, default=0)
    report_data = Column(JSON)
