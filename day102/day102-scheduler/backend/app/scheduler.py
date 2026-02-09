from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from croniter import croniter
from datetime import datetime
import pytz
import logging
from app.database import SessionLocal
from app.models import Job, Schedule, Execution
from app.event_bus import event_bus

logger = logging.getLogger(__name__)

class SchedulerEngine:
    def __init__(self):
        self.scheduler = BackgroundScheduler(timezone='UTC')
        
    def start(self):
        """Start the scheduler"""
        self.scheduler.start()
        logger.info("Scheduler engine started")
        
        # Load existing schedules
        self.load_schedules()
        
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler engine stopped")
    
    def load_schedules(self):
        """Load all active schedules from database"""
        db = SessionLocal()
        try:
            jobs = db.query(Job).filter(Job.enabled == True, Job.cron_expression != None).all()
            for job in jobs:
                self.add_schedule(job.id, job.cron_expression, job.timezone)
            logger.info(f"Loaded {len(jobs)} schedules")
        finally:
            db.close()
    
    def add_schedule(self, job_id: str, cron_expression: str, timezone: str = "UTC"):
        """Add a new schedule"""
        try:
            # Validate cron expression
            if not croniter.is_valid(cron_expression):
                raise ValueError(f"Invalid cron expression: {cron_expression}")
            
            # Create trigger
            tz = pytz.timezone(timezone)
            trigger = CronTrigger.from_crontab(cron_expression, timezone=tz)
            
            # Add job to scheduler
            self.scheduler.add_job(
                self.trigger_job,
                trigger=trigger,
                id=job_id,
                args=[job_id],
                replace_existing=True
            )
            
            logger.info(f"Added schedule for job {job_id}: {cron_expression}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add schedule for job {job_id}: {e}")
            return False
    
    def remove_schedule(self, job_id: str):
        """Remove a schedule"""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed schedule for job {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove schedule for job {job_id}: {e}")
            return False
    
    def trigger_job(self, job_id: str):
        """Trigger a job execution"""
        logger.info(f"Triggering job {job_id}")
        
        # Create execution record
        db = SessionLocal()
        try:
            execution = Execution(
                job_id=job_id,
                state="TRIGGERED",
                trigger_type="schedule"
            )
            db.add(execution)
            db.commit()
            
            # Publish trigger event
            event_bus.publish('job.triggered', 'job.triggered', {
                'execution_id': execution.id,
                'job_id': job_id,
                'trigger_type': 'schedule',
                'timestamp': datetime.utcnow().isoformat()
            })
            
        finally:
            db.close()

scheduler_engine = SchedulerEngine()
