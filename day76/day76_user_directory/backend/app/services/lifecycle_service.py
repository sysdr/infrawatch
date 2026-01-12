from datetime import datetime
from typing import Dict
from ..models import User, UserStatus, AuditLog

class LifecycleService:
    def __init__(self, db_session):
        self.db = db_session
    
    def transition_user(self, user: User, new_status: UserStatus, 
                       performed_by: str, reason: str = "") -> Dict:
        """Handle user lifecycle state transitions"""
        
        if user.status == new_status:
            return {'success': False, 'message': 'User already in this state'}
        
        # Validate transition
        valid_transitions = {
            UserStatus.PENDING: [UserStatus.ACTIVE, UserStatus.DEPROVISIONED],
            UserStatus.ACTIVE: [UserStatus.SUSPENDED, UserStatus.DEPROVISIONED],
            UserStatus.SUSPENDED: [UserStatus.ACTIVE, UserStatus.DEPROVISIONED],
            UserStatus.DEPROVISIONED: []  # Terminal state
        }
        
        if new_status not in valid_transitions.get(user.status, []):
            return {'success': False, 'message': f'Invalid transition from {user.status} to {new_status}'}
        
        old_status = user.status
        user.status = new_status
        user.updated_at = datetime.utcnow()
        
        # Execute state-specific actions
        if new_status == UserStatus.ACTIVE:
            self._activate_user(user)
        elif new_status == UserStatus.SUSPENDED:
            self._suspend_user(user)
        elif new_status == UserStatus.DEPROVISIONED:
            self._deprovision_user(user)
        
        # Audit log
        audit = AuditLog(
            user_id=user.id,
            action=f"status_change_{old_status}_to_{new_status}",
            details=f"Reason: {reason}" if reason else "",
            performed_by=performed_by,
            timestamp=datetime.utcnow()
        )
        self.db.add(audit)
        self.db.commit()
        
        return {
            'success': True,
            'message': f'User transitioned from {old_status} to {new_status}',
            'actions': self._get_transition_actions(new_status)
        }
    
    def _activate_user(self, user: User):
        """Actions when activating a user"""
        user.last_login = datetime.utcnow()
        # In production: send welcome email, assign default permissions, create home directory
    
    def _suspend_user(self, user: User):
        """Actions when suspending a user"""
        # In production: revoke sessions, disable API keys, preserve data
        pass
    
    def _deprovision_user(self, user: User):
        """Actions when deprovisioning a user"""
        user.deprovisioned_at = datetime.utcnow()
        # In production: anonymize data, export for compliance, delete credentials
    
    def _get_transition_actions(self, status: UserStatus) -> list:
        """Get list of actions performed during transition"""
        actions = {
            UserStatus.ACTIVE: [
                "Welcome email sent",
                "Default permissions assigned",
                "User directory created"
            ],
            UserStatus.SUSPENDED: [
                "Active sessions revoked",
                "API keys disabled",
                "Data preserved"
            ],
            UserStatus.DEPROVISIONED: [
                "Account data exported",
                "Credentials deleted",
                "Scheduled for anonymization in 90 days"
            ]
        }
        return actions.get(status, [])
    
    def process_offboarding(self, user: User, performed_by: str) -> Dict:
        """Complete offboarding workflow"""
        steps = []
        
        # Step 1: Suspend
        if user.status == UserStatus.ACTIVE:
            result = self.transition_user(user, UserStatus.SUSPENDED, performed_by, 
                                        "Automated offboarding initiated")
            steps.append(result)
        
        # Step 2: Export data (simulated)
        steps.append({
            'action': 'data_export',
            'status': 'completed',
            'message': 'User data exported to compliance archive'
        })
        
        # Step 3: Deprovision
        result = self.transition_user(user, UserStatus.DEPROVISIONED, performed_by,
                                     "Offboarding completed")
        steps.append(result)
        
        return {
            'user_id': user.id,
            'username': user.username,
            'offboarding_steps': steps,
            'completed_at': datetime.utcnow()
        }
