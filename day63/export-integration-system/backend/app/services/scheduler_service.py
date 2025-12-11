from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from app.database import get_db_context
from app.models.export_schedule import ExportSchedule
from workers.export_tasks import send_scheduled_export

class ExportScheduler:
    """Manages scheduled export execution"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler(timezone='UTC')
        self.scheduler.start()
    
    def start(self):
        """Load and schedule all active export schedules"""
        with get_db_context() as db:
            schedules = db.query(ExportSchedule).filter(ExportSchedule.enabled == True).all()
            
            for schedule in schedules:
                self.add_schedule(schedule)
    
    def add_schedule(self, schedule: ExportSchedule):
        """Add or update a scheduled export"""
        try:
            trigger = CronTrigger.from_crontab(schedule.schedule_expression, timezone=schedule.timezone)
            
            self.scheduler.add_job(
                send_scheduled_export,
                trigger=trigger,
                id=schedule.id,
                args=[schedule.id],
                replace_existing=True,
                max_instances=1
            )
            
            # Update next run time
            next_run = trigger.get_next_fire_time(None, datetime.now(trigger.timezone))
            schedule.next_run_at = next_run
            
        except Exception as e:
            print(f"Failed to schedule {schedule.id}: {e}")
    
    def remove_schedule(self, schedule_id: str):
        """Remove scheduled export"""
        try:
            self.scheduler.remove_job(schedule_id)
        except:
            pass
    
    def stop(self):
        """Stop scheduler"""
        self.scheduler.shutdown()

# Global scheduler instance
export_scheduler = ExportScheduler()
