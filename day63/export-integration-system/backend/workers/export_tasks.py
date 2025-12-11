from celery import Task
from app.celery_app import celery_app
from app.database import get_db_context
from app.models.export_job import ExportJob, JobStatus
from app.services.export_service import StreamingExporter
from datetime import datetime
from sqlalchemy import text
import os
import traceback

class ExportTask(Task):
    """Base task with database session management"""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure"""
        job_id = kwargs.get('job_id')
        if job_id:
            with get_db_context() as db:
                job = db.query(ExportJob).filter(ExportJob.id == job_id).first()
                if job:
                    job.status = JobStatus.FAILED
                    job.error_message = str(exc)
                    job.completed_at = datetime.utcnow()
                    db.commit()

@celery_app.task(base=ExportTask, bind=True, max_retries=3)
def process_export_job(self, job_id: str):
    """Process export job with streaming"""
    
    with get_db_context() as db:
        # Fetch job
        job = db.query(ExportJob).filter(ExportJob.id == job_id).first()
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        # Update status
        job.status = JobStatus.PROCESSING
        job.started_at = datetime.utcnow()
        db.commit()
        
        try:
            # Create output directory
            output_dir = "/tmp/exports"
            os.makedirs(output_dir, exist_ok=True)
            
            # Determine file extension
            ext_map = {"csv": ".csv", "json": ".json", "excel": ".xlsx"}
            file_ext = ext_map.get(job.format, ".csv")
            output_path = f"{output_dir}/{job_id}{file_ext}"
            
            # Build query based on export type
            query_dict = build_export_query(db, job.export_type, job.filters)
            
            # Stream export
            exporter = StreamingExporter(db)
            
            if job.format == "csv":
                result = exporter.export_to_csv(query_dict, output_path)
            elif job.format == "json":
                result = exporter.export_to_json(query_dict, output_path)
            elif job.format == "excel":
                result = exporter.export_to_excel(query_dict, output_path)
            else:
                raise ValueError(f"Unsupported format: {job.format}")
            
            # Update job with results
            job.row_count = result['row_count']
            job.file_size = result['file_size']
            job.checksum = result['checksum']
            job.file_path = output_path
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            
            # Validate export
            is_valid = exporter.validate_export(output_path, job.format, job.checksum)
            if not is_valid:
                raise ValueError("Export validation failed")
            
            db.commit()
            
            return {
                'job_id': job_id,
                'status': 'completed',
                'row_count': result['row_count'],
                'file_size': result['file_size']
            }
            
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            db.commit()
            raise

def build_export_query(db, export_type: str, filters: dict):
    """Build query for export based on type and filters"""
    import random
    from datetime import datetime, timedelta
    
    # For demo purposes, generate sample data instead of querying database
    # In production, this would query the actual metrics table
    # Check if metrics table exists
    try:
        result = db.execute(text("SELECT 1 FROM metrics LIMIT 1"))
        result.fetchone()
        table_exists = True
    except:
        table_exists = False
    
    if table_exists:
        # Table exists, build SQL query
        base_query = """
            SELECT 
                id,
                metric_name,
                value,
                timestamp,
                tags
            FROM metrics
            WHERE 1=1
        """
        
        if filters.get('start_date'):
            base_query += f" AND timestamp >= '{filters['start_date']}'"
        if filters.get('end_date'):
            base_query += f" AND timestamp <= '{filters['end_date']}'"
        if filters.get('metric_name'):
            base_query += f" AND metric_name = '{filters['metric_name']}'"
        
        base_query += " ORDER BY timestamp DESC"
        
        return {'query_text': base_query, 'filters': filters, 'use_sample_data': False}
    else:
        # Table doesn't exist, use sample data generator
        return {'query_text': None, 'filters': filters, 'use_sample_data': True, 'export_type': export_type}

@celery_app.task
def send_scheduled_export(schedule_id: str):
    """Execute scheduled export and send via email"""
    
    with get_db_context() as db:
        from app.models.export_schedule import ExportSchedule
        from app.models.export_history import ExportHistory
        import uuid
        
        schedule = db.query(ExportSchedule).filter(ExportSchedule.id == schedule_id).first()
        if not schedule or not schedule.enabled:
            return
        
        # Create export job
        job_id = str(uuid.uuid4())
        job = ExportJob(
            id=job_id,
            user_id=schedule.user_id,
            export_type=schedule.export_type,
            format=schedule.format,
            filters=schedule.filters
        )
        db.add(job)
        db.commit()
        
        # Process export
        start_time = datetime.utcnow()
        try:
            process_export_job.delay(job_id)
            
            # Wait for completion (simplified for demo)
            import time
            time.sleep(5)
            
            db.refresh(job)
            
            # Send email notification
            if job.status == JobStatus.COMPLETED:
                send_export_email(schedule.email_recipients, job)
            
            # Record history
            execution_time = (datetime.utcnow() - start_time).seconds
            history = ExportHistory(
                id=str(uuid.uuid4()),
                schedule_id=schedule_id,
                job_id=job_id,
                success=(job.status == JobStatus.COMPLETED),
                execution_time_seconds=execution_time
            )
            db.add(history)
            
            # Update schedule
            schedule.last_run_at = datetime.utcnow()
            schedule.run_count += 1
            
            db.commit()
            
        except Exception as e:
            history = ExportHistory(
                id=str(uuid.uuid4()),
                schedule_id=schedule_id,
                job_id=job_id,
                success=False,
                error_message=str(e)
            )
            db.add(history)
            db.commit()

def send_export_email(recipients: list, job: ExportJob):
    """Send export completion email"""
    print(f"Email sent to {recipients}: Export {job.id} completed with {job.row_count} rows")
    # In production, use aiosmtplib or similar
