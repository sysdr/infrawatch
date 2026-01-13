from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class ScanResult(Base):
    __tablename__ = "scan_results"
    
    id = Column(Integer, primary_key=True, index=True)
    scan_type = Column(String, index=True)  # vulnerability, dependency, compliance, threat
    severity = Column(String, index=True)  # CRITICAL, HIGH, MEDIUM, LOW
    title = Column(String)
    description = Column(Text)
    file_path = Column(String, nullable=True)
    line_number = Column(Integer, nullable=True)
    cve_id = Column(String, nullable=True)
    cvss_score = Column(Float, nullable=True)
    status = Column(String, default="open")  # open, in_progress, resolved, false_positive
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSON, default={})

class ComplianceCheck(Base):
    __tablename__ = "compliance_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    framework = Column(String, index=True)  # CIS, PCI_DSS, SOC2, GDPR
    control_id = Column(String)
    control_name = Column(String)
    description = Column(Text)
    status = Column(String)  # passed, failed, not_applicable
    severity = Column(String)
    evidence = Column(Text, nullable=True)
    remediation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ThreatModel(Base):
    __tablename__ = "threat_models"
    
    id = Column(Integer, primary_key=True, index=True)
    component_name = Column(String, index=True)
    threat_category = Column(String)  # STRIDE categories
    threat_description = Column(Text)
    likelihood = Column(Integer)  # 1-5
    impact = Column(Integer)  # 1-5
    risk_score = Column(Integer)  # likelihood * impact
    mitigation = Column(Text, nullable=True)
    status = Column(String, default="identified")  # identified, mitigated, accepted
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SecurityMetrics(Base):
    __tablename__ = "security_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String, index=True)
    metric_value = Column(Float)
    metric_type = Column(String)  # vulnerability_count, compliance_score, scan_coverage
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    meta_data = Column(JSON, default={})
