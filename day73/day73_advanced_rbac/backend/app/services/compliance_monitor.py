from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict
from ..models.permission_models import ComplianceViolation, UserRole, AuditEvent, User, Role
from sqlalchemy import func

class ComplianceMonitor:
    def __init__(self, db: Session):
        self.db = db
    
    def check_violations(self) -> List[ComplianceViolation]:
        """Check for compliance violations."""
        violations = []
        
        # Check 1: Privileged access duration
        violations.extend(self._check_privileged_access_duration())
        
        # Check 2: Unusual access patterns
        violations.extend(self._check_unusual_access())
        
        # Check 3: Bulk permission changes
        violations.extend(self._check_bulk_changes())
        
        return violations
    
    def _check_privileged_access_duration(self) -> List[ComplianceViolation]:
        """Alert if admin role held >24 hours."""
        violations = []
        cutoff = datetime.utcnow() - timedelta(hours=24)
        
        # Find users with admin role for >24 hours
        long_admins = self.db.query(UserRole).filter(
            UserRole.assigned_at < cutoff
        ).join(User, UserRole.user_id == User.id).all()
        
        for ur in long_admins:
            # Check if role is privileged (contains 'admin' or 'root')
            role = self.db.query(Role).filter(Role.id == ur.role_id).first()
            if role and ('admin' in role.name.lower() or 'root' in role.name.lower()):
                violation = ComplianceViolation(
                    violation_type='prolonged_privileged_access',
                    severity='high',
                    subject_id=f"user:{ur.user_id}",
                    description=f"User has held admin role for >24 hours",
                    detected_at=datetime.utcnow(),
                    violation_metadata={'role_id': ur.role_id, 'assigned_at': ur.assigned_at.isoformat()}
                )
                self.db.add(violation)
                violations.append(violation)
        
        return violations
    
    def _check_unusual_access(self) -> List[ComplianceViolation]:
        """Flag cross-environment access."""
        violations = []
        cutoff = datetime.utcnow() - timedelta(hours=24)
        
        # Find users accessing multiple environments
        cross_env_users = self.db.query(
            AuditEvent.subject_id,
            func.count(func.distinct(AuditEvent.resource_id)).label('env_count')
        ).filter(
            AuditEvent.timestamp >= cutoff,
            AuditEvent.resource_type == 'environment'
        ).group_by(AuditEvent.subject_id).having(
            func.count(func.distinct(AuditEvent.resource_id)) > 1
        ).all()
        
        for subject_id, env_count in cross_env_users:
            violation = ComplianceViolation(
                violation_type='cross_environment_access',
                severity='medium',
                subject_id=subject_id,
                description=f"User accessed {env_count} different environments in 24 hours",
                detected_at=datetime.utcnow(),
                violation_metadata={'environment_count': env_count}
            )
            self.db.add(violation)
            violations.append(violation)
        
        return violations
    
    def _check_bulk_changes(self) -> List[ComplianceViolation]:
        """Detect mass role assignments."""
        violations = []
        cutoff = datetime.utcnow() - timedelta(hours=1)
        
        # Find users who assigned >10 roles in 1 hour
        bulk_assigners = self.db.query(
            UserRole.assigned_by,
            func.count(UserRole.id).label('assignment_count')
        ).filter(
            UserRole.assigned_at >= cutoff
        ).group_by(UserRole.assigned_by).having(
            func.count(UserRole.id) > 10
        ).all()
        
        for assigner_id, count in bulk_assigners:
            if assigner_id:
                violation = ComplianceViolation(
                    violation_type='bulk_permission_changes',
                    severity='critical',
                    subject_id=f"user:{assigner_id}",
                    description=f"User assigned {count} roles in 1 hour (possible breach)",
                    detected_at=datetime.utcnow(),
                    violation_metadata={'assignment_count': count}
                )
                self.db.add(violation)
                violations.append(violation)
        
        return violations
    
    def get_active_violations(self) -> List[ComplianceViolation]:
        """Get unresolved violations."""
        return self.db.query(ComplianceViolation).filter(
            ComplianceViolation.resolved_at == None
        ).order_by(ComplianceViolation.detected_at.desc()).all()
    
    def resolve_violation(self, violation_id: int, notes: str):
        """Mark violation as resolved."""
        violation = self.db.query(ComplianceViolation).filter(
            ComplianceViolation.id == violation_id
        ).first()
        
        if violation:
            violation.resolved_at = datetime.utcnow()
            violation.resolution_notes = notes
            self.db.commit()
        
        return violation
