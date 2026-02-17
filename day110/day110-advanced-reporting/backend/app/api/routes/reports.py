from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.models.database import get_db, ReportDefinition, ReportTemplate, ReportExecution, ReportState
from app.api.schemas.report_schemas import ReportCreate, ReportResponse, ExecutionResponse, OutputFormat
from app.services.builders.report_builder import ReportBuilder
from app.services.builders.template_engine import TemplateEngine
from app.services.converters.pdf_converter import PDFConverter
from app.services.converters.excel_converter import ExcelConverter
from app.services.converters.csv_converter import CSVConverter
from app.services.converters.json_converter import JSONConverter
from datetime import datetime
import os

router = APIRouter()

@router.post("/", response_model=ReportResponse)
def create_report(report: ReportCreate, db: Session = Depends(get_db)):
    """Create a new report definition"""
    
    # Verify template exists
    template = db.query(ReportTemplate).filter(ReportTemplate.id == report.template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    db_report = ReportDefinition(
        name=report.name,
        template_id=report.template_id,
        parameters=report.parameters,
        output_formats=[fmt.value for fmt in report.output_formats],
        state=ReportState.DRAFT,
        created_by="system"
    )
    
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    
    return db_report

@router.get("/", response_model=list[ReportResponse])
def list_reports(db: Session = Depends(get_db)):
    """List all reports"""
    reports = db.query(ReportDefinition).all()
    return reports

@router.post("/{report_id}/generate")
async def generate_report(report_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Generate report in all configured formats"""
    
    report = db.query(ReportDefinition).filter(ReportDefinition.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    template = db.query(ReportTemplate).filter(ReportTemplate.id == report.template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Create execution record
    execution = ReportExecution(
        report_id=report_id,
        state=ReportState.GENERATING,
        started_at=datetime.utcnow()
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)
    
    # Generate in background (use new DB session inside task; request session would close)
    background_tasks.add_task(
        _generate_report_task,
        execution.id,
        report.id,
        report.template_id,
        report.parameters,
        report.output_formats,
    )
    
    return {"execution_id": execution.id, "status": "generating"}

def _generate_report_task(execution_id: int, report_id: int, template_id: int, parameters: dict, output_formats: list):
    """Background task to generate report (uses its own DB session)."""
    from app.models.database import SessionLocal
    
    db = SessionLocal()
    start_time = datetime.utcnow()
    
    try:
        report = db.query(ReportDefinition).filter(ReportDefinition.id == report_id).first()
        template = db.query(ReportTemplate).filter(ReportTemplate.id == template_id).first()
        if not report or not template:
            return
        
        # Build report data
        builder = ReportBuilder()
        data = builder.execute_query(template.query_config, parameters)
        
        # Get template structure
        engine = TemplateEngine()
        structure = engine.get_template_structure(template.layout_config)
        
        # Generate output directory (relative to backend CWD when uvicorn runs from backend/)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        output_dir = os.path.join(base_dir, "generated_reports", str(report_id))
        os.makedirs(output_dir, exist_ok=True)
        
        output_paths = {}
        
        # Generate each format
        for fmt in output_formats:
            output_path = os.path.join(output_dir, f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{fmt}")
            
            if fmt == "pdf":
                converter = PDFConverter()
                converter.convert(data, structure, output_path)
            elif fmt == "excel":
                converter = ExcelConverter()
                converter.convert(data, structure, output_path)
            elif fmt == "csv":
                converter = CSVConverter()
                converter.convert(data, structure, output_path)
            elif fmt == "json":
                converter = JSONConverter()
                converter.convert(data, structure, output_path)
            
            output_paths[fmt] = output_path
        
        # Update execution
        execution = db.query(ReportExecution).filter(ReportExecution.id == execution_id).first()
        if execution:
            execution.state = ReportState.COMPLETED
            execution.output_paths = output_paths
            execution.execution_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            execution.completed_at = datetime.utcnow()
            db.commit()
        
    except Exception as e:
        execution = db.query(ReportExecution).filter(ReportExecution.id == execution_id).first()
        if execution:
            execution.state = ReportState.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            db.commit()
    finally:
        db.close()

@router.get("/{report_id}/executions", response_model=list[ExecutionResponse])
def list_executions(report_id: int, db: Session = Depends(get_db)):
    """List all executions for a report"""
    executions = db.query(ReportExecution).filter(ReportExecution.report_id == report_id).order_by(ReportExecution.started_at.desc()).limit(10).all()
    return executions
