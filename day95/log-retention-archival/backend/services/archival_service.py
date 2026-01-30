from sqlalchemy.orm import Session
from models.log_entry import LogEntry, StorageTier, ArchivalJob, ComplianceAudit
from services.storage_service import storage_service
from datetime import datetime
import json
from typing import List, Dict

class ArchivalService:
    def __init__(self, db: Session):
        self.db = db
    
    def process_archival_job(self, job: ArchivalJob, transitions: List[Dict]) -> Dict:
        """Process log transitions for an archival job"""
        job.status = "running"
        self.db.commit()
        
        results = {
            "processed": 0,
            "failed": 0,
            "total_original_size": 0,
            "total_compressed_size": 0
        }
        
        try:
            for transition in transitions:
                try:
                    log = self.db.query(LogEntry).filter(LogEntry.id == transition["log_id"]).first()
                    if not log:
                        continue
                    
                    if transition["target_tier"] == StorageTier.DELETED:
                        self._delete_log(log)
                    else:
                        self._transition_log(log, transition["target_tier"])
                    
                    results["processed"] += 1
                    results["total_original_size"] += log.original_size or 0
                    results["total_compressed_size"] += log.compressed_size or 0
                    
                except Exception as e:
                    results["failed"] += 1
                    print(f"Error processing log {transition['log_id']}: {e}")
            
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            job.data_size = results["total_original_size"]
            job.compressed_size = results["total_compressed_size"]
            
        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
        
        self.db.commit()
        return results
    
    def _transition_log(self, log: LogEntry, target_tier: StorageTier):
        """Transition log to new storage tier"""
        # Simulate log data
        log_data = {
            "id": log.id,
            "source": log.source,
            "level": log.level,
            "message": log.message,
            "timestamp": log.timestamp.isoformat()
        }
        
        # Compress data
        compressed_data = storage_service.compress_data(json.dumps(log_data))
        checksum = storage_service.calculate_checksum(compressed_data)
        
        # Upload to new tier
        target_bucket = storage_service.get_bucket_for_tier(target_tier.value)
        object_name = f"{log.timestamp.strftime('%Y/%m/%d')}/{log.id}.gz"
        storage_path = storage_service.upload_log(target_bucket, object_name, compressed_data)
        
        # Delete from old tier if different
        if log.storage_path and log.storage_tier != target_tier:
            try:
                old_bucket = storage_service.get_bucket_for_tier(log.storage_tier.value)
                old_object = log.storage_path.split('/', 1)[1] if '/' in log.storage_path else log.storage_path
                storage_service.delete_log(old_bucket, old_object)
            except:
                pass
        
        # Update log metadata
        log.storage_tier = target_tier
        log.storage_path = storage_path
        log.original_size = len(json.dumps(log_data))
        log.compressed_size = len(compressed_data)
        log.compression_ratio = len(compressed_data) / log.original_size if log.original_size > 0 else 0
        log.checksum = checksum
        log.archived_at = datetime.utcnow()
        
        # Create compliance audit
        audit = ComplianceAudit(
            log_id=log.id,
            action="transitioned",
            actor="system",
            storage_tier=target_tier,
            compliance_check=True,
            extra_metadata={"from": log.storage_tier.value, "to": target_tier.value}
        )
        self.db.add(audit)
        self.db.commit()
    
    def _delete_log(self, log: LogEntry):
        """Delete log and create audit trail"""
        # Delete from storage
        if log.storage_path:
            try:
                bucket = storage_service.get_bucket_for_tier(log.storage_tier.value)
                object_name = log.storage_path.split('/', 1)[1] if '/' in log.storage_path else log.storage_path
                storage_service.delete_log(bucket, object_name)
            except:
                pass
        
        # Create deletion audit
        audit = ComplianceAudit(
            log_id=log.id,
            action="deleted",
            actor="system",
            storage_tier=log.storage_tier,
            compliance_check=True,
            extra_metadata={"retention_met": True, "deleted_at": datetime.utcnow().isoformat()}
        )
        self.db.add(audit)
        
        # Mark as deleted
        log.storage_tier = StorageTier.DELETED
        log.deleted_at = datetime.utcnow()
        self.db.commit()

def get_archival_service(db: Session):
    return ArchivalService(db)
