from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from models.database import get_db, init_db
from models.log_entry import LogEntry, RetentionPolicy, ArchivalJob, ComplianceAudit, StorageTier, ComplianceFramework, StorageMetrics
from services.retention_service import get_retention_service
from services.archival_service import get_archival_service
from services.cost_service import get_cost_service
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Optional
import uuid
import random

app = FastAPI(title="Log Retention & Archival System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class LogCreate(BaseModel):
    source: str
    level: str
    message: str

class PolicyCreate(BaseModel):
    name: str
    log_source_pattern: str
    log_level_pattern: Optional[str] = None
    hot_retention_days: int
    warm_retention_days: int
    cold_retention_days: int
    compliance_frameworks: List[str]
    auto_delete: bool = True

class RetentionResponse(BaseModel):
    transitions_found: int
    job_id: int
    estimated_logs: int

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()
    # Create default policies
    db = next(get_db())
    if db.query(RetentionPolicy).count() == 0:
        default_policies = [
            RetentionPolicy(
                name="Error Logs - SOC2",
                log_source_pattern=".*",
                log_level_pattern="error",
                hot_retention_days=7,
                warm_retention_days=90,
                cold_retention_days=2555,
                compliance_frameworks=["SOC2", "GDPR"],
                auto_delete=False
            ),
            RetentionPolicy(
                name="Access Logs - Standard",
                log_source_pattern="access.*",
                hot_retention_days=7,
                warm_retention_days=30,
                cold_retention_days=90,
                compliance_frameworks=["GDPR"],
                auto_delete=True
            )
        ]
        db.add_all(default_policies)
        db.commit()
    db.close()

@app.get("/")
def read_root():
    return {"message": "Log Retention & Archival System", "version": "1.0.0"}

@app.post("/logs", response_model=dict)
def create_log(log: LogCreate, db: Session = Depends(get_db)):
    """Create a new log entry"""
    log_entry = LogEntry(
        id=str(uuid.uuid4()),
        source=log.source,
        level=log.level,
        message=log.message,
        timestamp=datetime.utcnow(),
        storage_tier=StorageTier.HOT,
        original_size=len(log.message),
        compliance_tags=["SOC2"] if log.level == "error" else ["GDPR"]
    )
    
    db.add(log_entry)
    
    # Create audit
    audit = ComplianceAudit(
        log_id=log_entry.id,
        action="created",
        actor="api",
        storage_tier=StorageTier.HOT,
        compliance_check=True,
        extra_metadata={"source": log.source, "level": log.level}
    )
    db.add(audit)
    db.commit()
    
    return {"id": log_entry.id, "status": "created", "tier": "hot"}

@app.get("/logs", response_model=List[dict])
def get_logs(
    tier: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get logs with optional filters"""
    query = db.query(LogEntry).filter(LogEntry.deleted_at == None)
    
    if tier:
        query = query.filter(LogEntry.storage_tier == tier)
    if source:
        query = query.filter(LogEntry.source.contains(source))
    
    logs = query.order_by(LogEntry.timestamp.desc()).limit(limit).all()
    
    return [{
        "id": log.id,
        "source": log.source,
        "level": log.level,
        "message": log.message,
        "timestamp": log.timestamp.isoformat(),
        "storage_tier": log.storage_tier.value,
        "compressed_size": log.compressed_size,
        "compression_ratio": log.compression_ratio,
        "compliance_tags": log.compliance_tags
    } for log in logs]

@app.get("/logs/stats", response_model=dict)
def get_log_stats(db: Session = Depends(get_db)):
    """Get log statistics across tiers"""
    stats = {}
    
    for tier in [StorageTier.HOT, StorageTier.WARM, StorageTier.COLD]:
        count = db.query(LogEntry).filter(
            LogEntry.storage_tier == tier,
            LogEntry.deleted_at == None
        ).count()
        
        logs = db.query(LogEntry).filter(
            LogEntry.storage_tier == tier,
            LogEntry.deleted_at == None
        ).all()
        
        total_size = sum(log.compressed_size or log.original_size or 0 for log in logs)
        
        stats[tier.value] = {
            "count": count,
            "total_size_mb": round(total_size / (1024 ** 2), 2)
        }
    
    deleted_count = db.query(LogEntry).filter(LogEntry.deleted_at != None).count()
    stats["deleted"] = {"count": deleted_count}
    
    return stats

@app.post("/policies", response_model=dict)
def create_policy(policy: PolicyCreate, db: Session = Depends(get_db)):
    """Create retention policy"""
    db_policy = RetentionPolicy(
        name=policy.name,
        log_source_pattern=policy.log_source_pattern,
        log_level_pattern=policy.log_level_pattern,
        hot_retention_days=policy.hot_retention_days,
        warm_retention_days=policy.warm_retention_days,
        cold_retention_days=policy.cold_retention_days,
        compliance_frameworks=policy.compliance_frameworks,
        auto_delete=policy.auto_delete
    )
    
    db.add(db_policy)
    db.commit()
    
    return {"id": db_policy.id, "name": db_policy.name, "status": "created"}

@app.get("/policies", response_model=List[dict])
def get_policies(db: Session = Depends(get_db)):
    """Get all retention policies"""
    policies = db.query(RetentionPolicy).all()
    
    return [{
        "id": p.id,
        "name": p.name,
        "log_source_pattern": p.log_source_pattern,
        "hot_retention_days": p.hot_retention_days,
        "warm_retention_days": p.warm_retention_days,
        "cold_retention_days": p.cold_retention_days,
        "compliance_frameworks": p.compliance_frameworks,
        "auto_delete": p.auto_delete,
        "enabled": p.enabled
    } for p in policies]

@app.post("/retention/evaluate", response_model=RetentionResponse)
def evaluate_retention(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Evaluate retention policies and create archival job"""
    retention_svc = get_retention_service(db)
    transitions = retention_svc.evaluate_retention_policies()
    
    if not transitions:
        return RetentionResponse(
            transitions_found=0,
            job_id=0,
            estimated_logs=0
        )
    
    job = retention_svc.create_archival_job(transitions)
    
    # Process in background
    background_tasks.add_task(process_archival_background, job.id, transitions)
    
    return RetentionResponse(
        transitions_found=len(transitions),
        job_id=job.id,
        estimated_logs=len(transitions)
    )

def process_archival_background(job_id: int, transitions: List[dict]):
    """Background task to process archival"""
    db = next(get_db())
    job = db.query(ArchivalJob).filter(ArchivalJob.id == job_id).first()
    
    if job:
        archival_svc = get_archival_service(db)
        archival_svc.process_archival_job(job, transitions)
    
    db.close()

@app.get("/jobs", response_model=List[dict])
def get_jobs(limit: int = 20, db: Session = Depends(get_db)):
    """Get archival jobs"""
    jobs = db.query(ArchivalJob).order_by(ArchivalJob.created_at.desc()).limit(limit).all()
    
    return [{
        "id": j.id,
        "job_type": j.job_type,
        "status": j.status,
        "source_tier": j.source_tier.value if j.source_tier else None,
        "target_tier": j.target_tier.value if j.target_tier else None,
        "log_count": j.log_count,
        "data_size_mb": round((j.data_size or 0) / (1024 ** 2), 2),
        "compressed_size_mb": round((j.compressed_size or 0) / (1024 ** 2), 2),
        "started_at": j.started_at.isoformat() if j.started_at else None,
        "completed_at": j.completed_at.isoformat() if j.completed_at else None
    } for j in jobs]

@app.get("/costs", response_model=dict)
def get_costs(db: Session = Depends(get_db)):
    """Get storage costs"""
    cost_svc = get_cost_service(db)
    return cost_svc.calculate_storage_costs()

@app.get("/costs/recommendations", response_model=List[dict])
def get_cost_recommendations(db: Session = Depends(get_db)):
    """Get cost optimization recommendations"""
    cost_svc = get_cost_service(db)
    return cost_svc.get_cost_optimization_recommendations()

@app.get("/compliance/audit", response_model=List[dict])
def get_audit_trail(log_id: Optional[str] = None, limit: int = 100, db: Session = Depends(get_db)):
    """Get compliance audit trail"""
    query = db.query(ComplianceAudit)
    
    if log_id:
        query = query.filter(ComplianceAudit.log_id == log_id)
    
    audits = query.order_by(ComplianceAudit.created_at.desc()).limit(limit).all()
    
    return [{
        "id": a.id,
        "log_id": a.log_id,
        "action": a.action,
        "actor": a.actor,
        "storage_tier": a.storage_tier.value if a.storage_tier else None,
        "compliance_check": a.compliance_check,
        "metadata": a.extra_metadata,
        "created_at": a.created_at.isoformat()
    } for a in audits]

@app.post("/logs/generate", response_model=dict)
def generate_sample_logs(count: int = 100, db: Session = Depends(get_db)):
    """Generate sample logs for testing"""
    sources = ["api-server", "web-server", "database", "cache", "queue"]
    levels = ["info", "warning", "error", "debug"]
    messages = [
        "Request processed successfully",
        "Connection timeout",
        "Database query executed",
        "Cache miss",
        "Queue message processed"
    ]
    
    created = 0
    for i in range(count):
        # Create logs with varying ages
        age_days = random.randint(0, 100)
        timestamp = datetime.utcnow() - timedelta(days=age_days)
        
        log_entry = LogEntry(
            id=str(uuid.uuid4()),
            source=random.choice(sources),
            level=random.choice(levels),
            message=random.choice(messages),
            timestamp=timestamp,
            storage_tier=StorageTier.HOT if age_days < 7 else (StorageTier.WARM if age_days < 90 else StorageTier.COLD),
            original_size=random.randint(100, 1000),
            compliance_tags=["SOC2", "GDPR"]
        )
        
        db.add(log_entry)
        created += 1
    
    db.commit()
    
    return {"created": created, "status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
