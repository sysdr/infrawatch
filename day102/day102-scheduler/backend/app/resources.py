from app.database import SessionLocal
from app.models import ResourcePool, Execution, Job
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ResourceManager:
    def __init__(self):
        pass
    
    def can_allocate(self, requirements: dict) -> bool:
        """Check if resources can be allocated"""
        db = SessionLocal()
        try:
            for resource_type, amount in requirements.items():
                pool = db.query(ResourcePool).filter(ResourcePool.resource_type == resource_type).first()
                if not pool:
                    logger.warning(f"Resource pool {resource_type} not found")
                    return False
                
                available = pool.total_capacity - pool.allocated_capacity
                if available < amount:
                    logger.info(f"Insufficient {resource_type}: need {amount}, available {available}")
                    return False
            
            return True
        finally:
            db.close()
    
    def allocate_resources(self, execution_id: str, requirements: dict) -> bool:
        """Allocate resources for an execution"""
        db = SessionLocal()
        try:
            # Check if can allocate
            if not self.can_allocate(requirements):
                return False
            
            # Allocate resources
            for resource_type, amount in requirements.items():
                pool = db.query(ResourcePool).filter(ResourcePool.resource_type == resource_type).first()
                pool.allocated_capacity += amount
            
            # Update execution
            execution = db.query(Execution).filter(Execution.id == execution_id).first()
            execution.resource_allocation = requirements
            
            db.commit()
            logger.info(f"Allocated resources for execution {execution_id}: {requirements}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to allocate resources: {e}")
            return False
        finally:
            db.close()
    
    def release_resources(self, execution_id: str):
        """Release resources from an execution"""
        db = SessionLocal()
        try:
            execution = db.query(Execution).filter(Execution.id == execution_id).first()
            if not execution or not execution.resource_allocation:
                return
            
            # Release resources
            for resource_type, amount in execution.resource_allocation.items():
                pool = db.query(ResourcePool).filter(ResourcePool.resource_type == resource_type).first()
                if pool:
                    pool.allocated_capacity = max(0, pool.allocated_capacity - amount)
            
            db.commit()
            logger.info(f"Released resources for execution {execution_id}")
            
            # Try to allocate queued jobs
            self.process_queue()
            
        finally:
            db.close()
    
    def process_queue(self):
        """Process queued executions and allocate resources if available"""
        db = SessionLocal()
        try:
            queued = db.query(Execution).filter(Execution.state == "QUEUED").order_by(Execution.created_at).all()
            
            for execution in queued:
                job = db.query(Job).filter(Job.id == execution.job_id).first()
                if self.allocate_resources(execution.id, job.resources):
                    # Update state and dispatch
                    execution.state = "RUNNING"
                    execution.start_time = datetime.utcnow()
                    db.commit()
                    
                    # Sync execution for demo (no Celery required)
                    from app.tasks import execute_job
                    execute_job(execution.id, job.id, job.command)
                    
        finally:
            db.close()
    
    def get_utilization(self) -> dict:
        """Get current resource utilization"""
        db = SessionLocal()
        try:
            pools = db.query(ResourcePool).all()
            utilization = {}
            
            for pool in pools:
                utilization[pool.resource_type] = {
                    'total': pool.total_capacity,
                    'allocated': pool.allocated_capacity,
                    'available': pool.total_capacity - pool.allocated_capacity,
                    'utilization_pct': (pool.allocated_capacity / pool.total_capacity) * 100 if pool.total_capacity > 0 else 0
                }
            
            return utilization
        finally:
            db.close()

resource_manager = ResourceManager()
