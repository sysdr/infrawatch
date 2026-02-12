from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.models.security import SecurityCheck, SecurityViolation, ViolationSeverity

router = APIRouter()

class SecurityCheckResponse(BaseModel):
    id: int
    execution_id: int
    check_type: str
    passed: bool
    details: dict
    timestamp: datetime
    
    class Config:
        from_attributes = True

class SecurityViolationResponse(BaseModel):
    id: int
    execution_id: int
    violation_type: str
    severity: str
    description: str
    details: dict
    remediation: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

class SecurityStatsResponse(BaseModel):
    total_checks: int
    passed_checks: int
    failed_checks: int
    total_violations: int
    critical_violations: int
    high_violations: int

@router.get("/checks/{execution_id}", response_model=List[SecurityCheckResponse])
async def get_security_checks(execution_id: int, db: AsyncSession = Depends(get_db)):
    """Get security checks for an execution"""
    result = await db.execute(
        select(SecurityCheck)
        .where(SecurityCheck.execution_id == execution_id)
        .order_by(SecurityCheck.timestamp)
    )
    checks = result.scalars().all()
    return checks

@router.get("/violations", response_model=List[SecurityViolationResponse])
async def list_violations(db: AsyncSession = Depends(get_db)):
    """List all security violations"""
    result = await db.execute(
        select(SecurityViolation).order_by(SecurityViolation.timestamp.desc()).limit(100)
    )
    violations = result.scalars().all()
    return violations

@router.get("/stats", response_model=SecurityStatsResponse)
async def get_security_stats(db: AsyncSession = Depends(get_db)):
    """Get security statistics"""
    # Total checks
    total_checks_result = await db.execute(select(func.count(SecurityCheck.id)))
    total_checks = total_checks_result.scalar() or 0
    
    # Passed checks
    passed_checks_result = await db.execute(
        select(func.count(SecurityCheck.id)).where(SecurityCheck.passed == True)
    )
    passed_checks = passed_checks_result.scalar() or 0
    
    # Total violations
    total_violations_result = await db.execute(select(func.count(SecurityViolation.id)))
    total_violations = total_violations_result.scalar() or 0
    
    # Critical violations
    critical_result = await db.execute(
        select(func.count(SecurityViolation.id)).where(SecurityViolation.severity == ViolationSeverity.CRITICAL)
    )
    critical_violations = critical_result.scalar() or 0
    
    # High violations
    high_result = await db.execute(
        select(func.count(SecurityViolation.id)).where(SecurityViolation.severity == ViolationSeverity.HIGH)
    )
    high_violations = high_result.scalar() or 0
    
    return SecurityStatsResponse(
        total_checks=total_checks,
        passed_checks=passed_checks,
        failed_checks=total_checks - passed_checks,
        total_violations=total_violations,
        critical_violations=critical_violations,
        high_violations=high_violations
    )
