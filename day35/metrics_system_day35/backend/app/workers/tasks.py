from celery import current_task
from .celery_app import celery_app
from ..database import SessionLocal
from ..models import Task, TaskStatus, TaskResult
from ..services.metrics_processor import MetricsProcessor
import json
import time
import traceback
from datetime import datetime
import pandas as pd
import io

@celery_app.task(bind=True)
def process_metrics_task(self, task_id: str):
    """Process a metrics collection task"""
    db = SessionLocal()
    processor = MetricsProcessor()
    
    try:
        # Get task from database
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise Exception(f"Task {task_id} not found")
        
        # Update task status
        task.status = TaskStatus.PROCESSING
        task.started_at = datetime.utcnow()
        task.worker_id = self.request.id
        db.commit()
        
        # Update progress
        self.update_state(state='PROGRESS', meta={'progress': 10})
        
        # Process based on task type
        if task.task_type == "collect_system_metrics":
            result = processor.collect_system_metrics()
        elif task.task_type == "process_csv":
            result = processor.process_csv_file(task.payload)
        elif task.task_type == "generate_report":
            result = processor.generate_metrics_report(task.payload)
        else:
            raise Exception(f"Unknown task type: {task.task_type}")
        
        self.update_state(state='PROGRESS', meta={'progress': 50})
        
        # Simulate processing time
        time.sleep(2)
        
        self.update_state(state='PROGRESS', meta={'progress': 90})
        
        # Save result
        task_result = TaskResult(
            task_id=task_id,
            result_data=result,
            metrics={
                "execution_time": time.time() - task.started_at.timestamp(),
                "records_processed": result.get("records_count", 0)
            }
        )
        db.add(task_result)
        
        # Update task
        task.status = TaskStatus.SUCCESS
        task.completed_at = datetime.utcnow()
        task.result = result
        task.execution_time = time.time() - task.started_at.timestamp()
        
        db.commit()
        
        self.update_state(state='SUCCESS', meta={'progress': 100, 'result': result})
        return result
        
    except Exception as e:
        # Handle failure
        task.status = TaskStatus.FAILED
        task.error_message = str(e)
        task.completed_at = datetime.utcnow()
        
        # Implement retry logic
        if task.retry_count < task.max_retries:
            task.retry_count += 1
            task.status = TaskStatus.RETRY
            db.commit()
            
            # Retry with exponential backoff
            retry_delay = (2 ** task.retry_count) * 60
            self.retry(countdown=retry_delay, max_retries=task.max_retries)
        else:
            db.commit()
        
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'traceback': traceback.format_exc()}
        )
        raise
    finally:
        db.close()

@celery_app.task(bind=True)
def process_csv_task(self, task_id: str):
    """Process CSV file asynchronously"""
    db = SessionLocal()
    
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise Exception(f"Task {task_id} not found")
        
        task.status = TaskStatus.PROCESSING
        task.started_at = datetime.utcnow()
        db.commit()
        
        # Process CSV in chunks
        file_content = task.payload.get("file_content")
        chunk_size = task.payload.get("chunk_size", 1000)
        
        df = pd.read_csv(io.StringIO(file_content))
        total_rows = len(df)
        processed_rows = 0
        results = []
        
        for chunk in pd.read_csv(io.StringIO(file_content), chunksize=chunk_size):
            # Process each chunk
            chunk_result = process_csv_chunk(chunk)
            results.extend(chunk_result)
            
            processed_rows += len(chunk)
            progress = int((processed_rows / total_rows) * 100)
            
            self.update_state(
                state='PROGRESS',
                meta={'progress': progress, 'processed_rows': processed_rows}
            )
        
        # Save final result
        result = {
            "total_rows": total_rows,
            "processed_rows": processed_rows,
            "results": results[:100]  # Limit results for response size
        }
        
        task.status = TaskStatus.SUCCESS
        task.result = result
        task.completed_at = datetime.utcnow()
        task.execution_time = time.time() - task.started_at.timestamp()
        
        db.commit()
        return result
        
    except Exception as e:
        task.status = TaskStatus.FAILED
        task.error_message = str(e)
        task.completed_at = datetime.utcnow()
        db.commit()
        raise
    finally:
        db.close()

def process_csv_chunk(chunk):
    """Process a chunk of CSV data"""
    # Example processing: calculate statistics
    return {
        "chunk_size": len(chunk),
        "columns": list(chunk.columns),
        "numeric_summary": chunk.describe().to_dict() if not chunk.empty else {}
    }
