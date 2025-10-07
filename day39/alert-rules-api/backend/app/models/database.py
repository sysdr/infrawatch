from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
import os
import asyncio
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./alert_rules.db")

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AlertRule(Base):
    __tablename__ = "alert_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text)
    expression = Column(Text, nullable=False)
    severity = Column(String(50), default="warning")
    enabled = Column(Boolean, default=True)
    template_id = Column(Integer, nullable=True)
    tags = Column(JSON, default=list)
    thresholds = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    created_by = Column(String(255), default="system")

class RuleTemplate(Base):
    __tablename__ = "rule_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    category = Column(String(100), nullable=False)
    template_config = Column(JSON, nullable=False)
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

class RuleTest(Base):
    __tablename__ = "rule_tests"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, nullable=False)
    test_data = Column(JSON, nullable=False)
    expected_result = Column(Boolean, nullable=False)
    actual_result = Column(Boolean, nullable=True)
    test_status = Column(String(50), default="pending")
    executed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully")
