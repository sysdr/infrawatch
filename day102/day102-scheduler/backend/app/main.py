import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session

from app.database import init_db, get_db, SessionLocal
from app.models import Job, Execution, Schedule, ResourcePool
from app.resources import resource_manager
from app.dependency import dependency_resolver

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    logger.info("Shutting down...")

app = FastAPI(title="Scheduler API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class JobCreate(BaseModel):
    name: str
    command: str
    cron_expression: Optional[str] = None
    timezone: str = "UTC"

@app.get("/")
async def root():
    return {"message": "Day 102: Scheduling & Triggers API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/dashboard")
async def get_dashboard(db: Session = Depends(get_db)):
    """Dashboard metrics - populated by demo"""
    jobs = db.query(Job).count()
    executions = db.query(Execution).count()
    completed = db.query(Execution).filter(Execution.state == "COMPLETED").count()
    failed = db.query(Execution).filter(Execution.state == "FAILED").count()
    running = db.query(Execution).filter(Execution.state == "RUNNING").count()
    utilization = resource_manager.get_utilization()
    return {
        "jobs": jobs,
        "executions": executions,
        "completed": completed,
        "failed": failed,
        "running": running,
        "utilization": utilization
    }

@app.post("/api/jobs", response_model=dict)
async def create_job(job: JobCreate, db: Session = Depends(get_db)):
    existing = db.query(Job).filter(Job.name == job.name).first()
    if existing:
        raise HTTPException(400, "Job name already exists")
    j = Job(name=job.name, command=job.command, cron_expression=job.cron_expression, timezone=job.timezone)
    db.add(j)
    db.commit()
    db.refresh(j)
    return {"id": j.id, "name": j.name}

@app.get("/api/jobs")
async def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(Job).all()
    return [{"id": j.id, "name": j.name, "command": j.command, "enabled": j.enabled} for j in jobs]

@app.post("/api/jobs/{job_id}/trigger")
async def trigger_job(job_id: str, db: Session = Depends(get_db)):
    from app.tasks import execute_job
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(404, "Job not found")
    deps_ok, msg = dependency_resolver.check_dependencies(job_id)
    if not deps_ok:
        raise HTTPException(400, msg)
    exec_rec = Execution(job_id=job_id, state="TRIGGERED", trigger_type="manual")
    db.add(exec_rec)
    db.commit()
    if resource_manager.can_allocate(job.resources or {"cpu": 1, "memory": 512}):
        resource_manager.allocate_resources(exec_rec.id, job.resources or {"cpu": 1, "memory": 512})
        exec_rec.state = "RUNNING"
        exec_rec.start_time = __import__("datetime").datetime.utcnow()
        db.commit()
        execute_job(exec_rec.id, job_id, job.command)
    else:
        exec_rec.state = "QUEUED"
        db.commit()
    return {"execution_id": exec_rec.id, "state": exec_rec.state}

@app.get("/api/executions")
async def list_executions(db: Session = Depends(get_db)):
    ex = db.query(Execution).order_by(Execution.created_at.desc()).limit(50).all()
    return [{"id": e.id, "job_id": e.job_id, "state": e.state, "trigger_type": e.trigger_type} for e in ex]
