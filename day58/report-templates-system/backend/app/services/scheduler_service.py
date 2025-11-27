from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.template import ScheduledReport
from app.services.report_service import ReportService
from app.services.email_service import EmailService
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SchedulerService:
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.email_service = EmailService()
    
    def start(self):
        """Start the scheduler"""
        self.scheduler.add_job(
            self.check_scheduled_reports,
            'interval',
            minutes=1,
            id='check_scheduled_reports'
        )
        self.scheduler.start()
        logger.info("Scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")
    
    def check_scheduled_reports(self):
        """Check for reports that need to be generated"""
        db = SessionLocal()
        try:
            now = datetime.utcnow()
            due_reports = db.query(ScheduledReport).filter(
                ScheduledReport.is_active == True,
                ScheduledReport.next_run <= now
            ).all()
            
            logger.info(f"Found {len(due_reports)} reports due for generation")
            
            for report in due_reports:
                try:
                    # Generate report
                    execution = ReportService.generate_report(db, report.id)
                    logger.info(f"Generated report {report.name} (execution_id={execution.id})")
                    
                    # Send emails
                    deliveries = self.email_service.send_report(
                        db, execution.id, report.recipients
                    )
                    logger.info(f"Sent report to {len(deliveries)} recipients")
                    
                except Exception as e:
                    logger.error(f"Failed to process report {report.id}: {str(e)}")
        
        finally:
            db.close()
