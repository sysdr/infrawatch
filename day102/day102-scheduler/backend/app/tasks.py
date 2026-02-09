import subprocess
import logging
from datetime import datetime
from app.database import SessionLocal
from app.models import Execution
from app.resources import resource_manager
from app.dependency import dependency_resolver

logger = logging.getLogger(__name__)

def execute_job(execution_id: str, job_id: str, command: str):
    """Execute job synchronously - for demo without Celery"""
    db = SessionLocal()
    try:
        execution = db.query(Execution).filter(Execution.id == execution_id).first()
        if not execution:
            return
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            execution.state = "COMPLETED"
            execution.exit_code = result.returncode
            execution.logs = result.stdout[:5000] if result.stdout else (result.stderr[:5000] if result.stderr else "OK")
        except subprocess.TimeoutExpired:
            execution.state = "TIMEOUT"
            execution.logs = "Job timed out"
        except Exception as e:
            execution.state = "FAILED"
            execution.logs = str(e)
        execution.end_time = datetime.utcnow()
        db.commit()
        resource_manager.release_resources(execution_id)
        dependency_resolver.notify_downstream(job_id, execution.state)
    finally:
        db.close()
