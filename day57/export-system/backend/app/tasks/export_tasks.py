from app.celery_config import celery_app
from sqlalchemy.orm import Session
from app.models.database import SessionLocal
from app.models.notification import Notification
from app.models.export_job import ExportJob, ExportStatus, ExportFormat
from app.services.csv_export import CSVExportService
from app.services.json_export import JSONExportService
from app.services.pdf_export import PDFExportService
from app.services.excel_export import ExcelExportService
from datetime import datetime, timedelta
import os
import uuid

BATCH_SIZE = 1000
EXPORT_STORAGE_PATH = os.getenv("EXPORT_STORAGE_PATH", "./exports")

@celery_app.task(bind=True)
def generate_export(self, job_id: str):
    db = SessionLocal()
    try:
        job = db.query(ExportJob).filter(ExportJob.job_id == job_id).first()
        if not job:
            return {"error": "Job not found"}
            
        # Update status to processing
        job.status = ExportStatus.PROCESSING
        job.started_at = datetime.utcnow()
        db.commit()
        
        # Get total count
        query = db.query(Notification)
        if job.filters:
            if job.filters.get("user_id"):
                query = query.filter(Notification.user_id == job.filters["user_id"])
            if job.filters.get("notification_type"):
                query = query.filter(Notification.notification_type == job.filters["notification_type"])
            if job.filters.get("start_date"):
                query = query.filter(Notification.created_at >= job.filters["start_date"])
            if job.filters.get("end_date"):
                query = query.filter(Notification.created_at <= job.filters["end_date"])
                
        total_records = query.count()
        job.total_records = total_records
        db.commit()
        
        # Initialize export service based on format
        if job.export_format == ExportFormat.CSV:
            service = CSVExportService()
            service.initialize(['id', 'user_id', 'title', 'message', 'notification_type', 'is_read', 'created_at'])
        elif job.export_format == ExportFormat.JSON:
            service = JSONExportService()
            service.initialize({
                'total': total_records,
                'exported_at': datetime.utcnow().isoformat(),
                'format': 'json'
            })
        elif job.export_format == ExportFormat.PDF:
            service = PDFExportService()
            service.initialize('Notification Export Report', {'total_records': total_records})
        elif job.export_format == ExportFormat.EXCEL:
            service = ExcelExportService()
            service.initialize(['id', 'user_id', 'title', 'message', 'notification_type', 'is_read', 'created_at'])
        else:
            raise ValueError(f"Unsupported format: {job.export_format}")
            
        # Process in batches
        offset = 0
        processed = 0
        
        while offset < total_records:
            batch = query.offset(offset).limit(BATCH_SIZE).all()
            if not batch:
                break
                
            # Convert to dict
            batch_data = []
            for notification in batch:
                batch_data.append({
                    'id': notification.id,
                    'user_id': notification.user_id,
                    'title': notification.title,
                    'message': notification.message,
                    'notification_type': notification.notification_type.value,
                    'is_read': notification.is_read,
                    'created_at': notification.created_at
                })
                
            # Write batch
            if job.export_format in [ExportFormat.CSV, ExportFormat.JSON, ExportFormat.EXCEL]:
                service.write_batch(batch_data)
            elif job.export_format == ExportFormat.PDF:
                service.write_batch(batch_data, ['id', 'user_id', 'title', 'message', 'type', 'read', 'created'])
                
            processed += len(batch)
            offset += BATCH_SIZE
            
            # Update progress
            job.processed_records = processed
            db.commit()
            
            self.update_state(
                state='PROGRESS',
                meta={'current': processed, 'total': total_records, 'percent': int((processed / total_records) * 100)}
            )
            
        # Finalize export
        if job.export_format == ExportFormat.PDF:
            service.finalize()
            
        # Save file
        os.makedirs(EXPORT_STORAGE_PATH, exist_ok=True)
        file_extension = job.export_format.value
        filename = f"{job_id}.{file_extension}"
        file_path = os.path.join(EXPORT_STORAGE_PATH, filename)
        
        if job.export_format in [ExportFormat.PDF, ExportFormat.EXCEL]:
            content = service.get_content()
            with open(file_path, 'wb') as f:
                f.write(content)
            file_size = len(content)
        else:
            content = service.get_content()
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            file_size = len(content.encode('utf-8'))
            
        service.close()
        
        # Update job
        job.status = ExportStatus.COMPLETED
        job.file_path = file_path
        job.file_size = file_size
        job.download_url = f"/api/exports/{job_id}/download"
        job.completed_at = datetime.utcnow()
        job.expires_at = datetime.utcnow() + timedelta(hours=int(os.getenv("EXPORT_EXPIRY_HOURS", "24")))
        db.commit()
        
        return {
            "status": "completed",
            "job_id": job_id,
            "records": processed,
            "file_size": file_size
        }
        
    except Exception as e:
        job.status = ExportStatus.FAILED
        job.error_message = str(e)
        job.retry_count += 1
        db.commit()
        raise
    finally:
        db.close()
