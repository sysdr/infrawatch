from sqlalchemy.orm import Session
from models.log_entry import LogEntry, RetentionPolicy, StorageTier, ArchivalJob, ComplianceAudit
from datetime import datetime, timedelta
from typing import List, Dict
from config.settings import settings
import re

class RetentionService:
    def __init__(self, db: Session):
        self.db = db
    
    def evaluate_retention_policies(self) -> List[Dict]:
        """Identify logs that need tier transition"""
        policies = self.db.query(RetentionPolicy).filter(RetentionPolicy.enabled == True).all()
        transitions = []
        
        for policy in policies:
            # Find logs matching this policy
            logs = self._find_matching_logs(policy)
            
            for log in logs:
                transition = self._evaluate_log_transition(log, policy)
                if transition:
                    transitions.append(transition)
        
        return transitions
    
    def _find_matching_logs(self, policy: RetentionPolicy) -> List[LogEntry]:
        query = self.db.query(LogEntry).filter(LogEntry.deleted_at == None)
        
        if policy.log_source_pattern:
            # Simple pattern matching
            logs = query.all()
            matching = [log for log in logs if re.match(policy.log_source_pattern, log.source)]
            return matching
        
        return query.limit(settings.BATCH_SIZE).all()
    
    def _evaluate_log_transition(self, log: LogEntry, policy: RetentionPolicy) -> Dict:
        now = datetime.utcnow()
        log_age_days = (now - log.timestamp).days
        
        # Determine target tier based on age
        if log.storage_tier == StorageTier.HOT and log_age_days >= policy.hot_retention_days:
            return {
                "log_id": log.id,
                "source_tier": StorageTier.HOT,
                "target_tier": StorageTier.WARM,
                "policy_id": policy.id,
                "age_days": log_age_days
            }
        
        elif log.storage_tier == StorageTier.WARM and log_age_days >= policy.warm_retention_days:
            return {
                "log_id": log.id,
                "source_tier": StorageTier.WARM,
                "target_tier": StorageTier.COLD,
                "policy_id": policy.id,
                "age_days": log_age_days
            }
        
        elif log.storage_tier == StorageTier.COLD and log_age_days >= policy.cold_retention_days:
            if policy.auto_delete:
                return {
                    "log_id": log.id,
                    "source_tier": StorageTier.COLD,
                    "target_tier": StorageTier.DELETED,
                    "policy_id": policy.id,
                    "age_days": log_age_days
                }
        
        return None
    
    def create_archival_job(self, transitions: List[Dict]) -> ArchivalJob:
        job = ArchivalJob(
            job_type="transition",
            status="pending",
            source_tier=transitions[0]["source_tier"] if transitions else StorageTier.HOT,
            target_tier=transitions[0]["target_tier"] if transitions else StorageTier.WARM,
            log_count=len(transitions),
            started_at=datetime.utcnow()
        )
        self.db.add(job)
        self.db.commit()
        return job

retention_service = None

def get_retention_service(db: Session):
    return RetentionService(db)
