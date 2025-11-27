from sqlalchemy.orm import Session
from app.models.template import ScheduledReport, ReportExecution, ReportStatus, Template
from app.services.template_service import TemplateService
from datetime import datetime, timedelta
from typing import Dict, Any
import os
from weasyprint import HTML
import json

class ReportService:
    
    @staticmethod
    def create_scheduled_report(db: Session, template_id: int, name: str,
                               schedule_cron: str, recipients: list,
                               config: dict = None) -> ScheduledReport:
        """Create a scheduled report"""
        scheduled_report = ScheduledReport(
            template_id=template_id,
            name=name,
            schedule_cron=schedule_cron,
            recipients=recipients,
            config=config or {},
            next_run=ReportService.calculate_next_run(schedule_cron)
        )
        db.add(scheduled_report)
        db.commit()
        db.refresh(scheduled_report)
        return scheduled_report
    
    @staticmethod
    def calculate_next_run(cron_expression: str) -> datetime:
        """Calculate next run time from cron expression"""
        # Simplified for demo - in production use croniter
        return datetime.utcnow() + timedelta(hours=24)
    
    @staticmethod
    def generate_report(db: Session, scheduled_report_id: int,
                       data: Dict[str, Any] = None) -> ReportExecution:
        """Generate a report"""
        scheduled_report = db.query(ScheduledReport).filter(
            ScheduledReport.id == scheduled_report_id
        ).first()
        
        if not scheduled_report:
            raise ValueError("Scheduled report not found")
        
        # Create execution record
        execution = ReportExecution(
            scheduled_report_id=scheduled_report_id,
            status=ReportStatus.PROCESSING,
            started_at=datetime.utcnow()
        )
        db.add(execution)
        db.commit()
        
        try:
            # Get template
            template = scheduled_report.template
            if not template:
                raise ValueError(f"Template with id {scheduled_report.template_id} not found")
            
            # Generate sample data if not provided
            if data is None:
                data = ReportService.generate_sample_data(scheduled_report.config)
            
            # Render template
            html_content = TemplateService.render_template(template, data)
            
            # Save output
            output_dir = os.getenv("STORAGE_PATH", "../outputs")
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            base_filename = f"report_{execution.id}_{timestamp}"
            
            # Save HTML
            html_file = f"{output_dir}/{base_filename}.html"
            with open(html_file, 'w') as f:
                f.write(html_content)
            
            execution.output_file = html_file
            execution.output_format = "html"
            
            # Generate PDF if needed
            if template.format in ["pdf", "both"]:
                pdf_file = f"{output_dir}/{base_filename}.pdf"
                HTML(string=html_content).write_pdf(pdf_file)
                execution.output_file = pdf_file
                execution.output_format = "pdf"
            
            # Mark as completed
            execution.status = ReportStatus.COMPLETED
            execution.completed_at = datetime.utcnow()
            execution.execution_time = int((execution.completed_at - execution.started_at).total_seconds())
            
            # Update scheduled report
            scheduled_report.last_run = datetime.utcnow()
            scheduled_report.next_run = ReportService.calculate_next_run(scheduled_report.schedule_cron)
            
            db.commit()
            db.refresh(execution)
            return execution
            
        except Exception as e:
            execution.status = ReportStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            db.commit()
            raise
    
    @staticmethod
    def generate_sample_data(config: dict) -> Dict[str, Any]:
        """Generate sample data for report"""
        return {
            "company_name": "TechCorp Inc.",
            "report_type": "Weekly Summary",
            "date_range": "Nov 18-24, 2025",
            "recipient_name": "Team",
            "total_alerts": 1247,
            "critical_alerts": 23,
            "warning_alerts": 156,
            "info_alerts": 1068,
            "top_services": [
                {"name": "API Gateway", "count": 342, "severity": "critical"},
                {"name": "Database Cluster", "count": 289, "severity": "warning"},
                {"name": "Cache Service", "count": 234, "severity": "info"}
            ],
            "performance_metrics": {
                "avg_response_time": "245ms",
                "uptime": "99.94%",
                "error_rate": "0.12%"
            },
            "trends": {
                "alerts_vs_last_week": "+15%",
                "response_time_change": "-8%",
                "uptime_change": "+0.02%"
            }
        }
    
    @staticmethod
    def get_executions(db: Session, scheduled_report_id: int = None,
                      status: ReportStatus = None, limit: int = 100):
        """Get report executions"""
        query = db.query(ReportExecution)
        if scheduled_report_id:
            query = query.filter(ReportExecution.scheduled_report_id == scheduled_report_id)
        if status:
            query = query.filter(ReportExecution.status == status)
        return query.order_by(ReportExecution.started_at.desc()).limit(limit).all()
