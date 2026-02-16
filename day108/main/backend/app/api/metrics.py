from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Dict
from pydantic import BaseModel, Field
from app.services.metric_engine import MetricEngine
from app.models.metric import MetricDefinition
import json

router = APIRouter(prefix="/api/metrics", tags=["metrics"])

# Database dependency
def get_db():
    from app.main import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models
class MetricCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    display_name: str = Field(..., min_length=1)
    description: str = ""
    formula: str = Field(..., min_length=1)
    variables: List[str] = Field(..., min_items=1)
    category: str = "custom"
    unit: str = ""
    aggregation_type: str = "sum"
    validation_rules: Dict = {}
    created_by: str = "system"

class MetricCalculate(BaseModel):
    input_values: Dict[str, float]

class FormulaValidate(BaseModel):
    formula: str
    variables: List[str]

@router.post("/definitions")
async def create_metric(metric: MetricCreate, db: Session = Depends(get_db)):
    """Create a new metric definition"""
    engine = MetricEngine(db)
    try:
        result = await engine.create_metric(metric.dict())
        return {
            "id": result.id,
            "name": result.name,
            "formula": result.formula,
            "message": "Metric created successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Metric '{metric.name}' already exists")

@router.get("/definitions")
async def list_metrics(db: Session = Depends(get_db)):
    """List all metric definitions"""
    metrics = db.query(MetricDefinition).filter_by(is_active=True).all()
    return [
        {
            "id": m.id,
            "name": m.name,
            "display_name": m.display_name,
            "description": m.description,
            "formula": m.formula,
            "variables": m.variables,
            "category": m.category,
            "unit": m.unit,
            "created_at": m.created_at.isoformat()
        }
        for m in metrics
    ]

@router.get("/definitions/{metric_id}")
async def get_metric(metric_id: str, db: Session = Depends(get_db)):
    """Get a specific metric definition"""
    metric = db.query(MetricDefinition).filter_by(id=metric_id).first()
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")
    
    return {
        "id": metric.id,
        "name": metric.name,
        "display_name": metric.display_name,
        "description": metric.description,
        "formula": metric.formula,
        "variables": metric.variables,
        "category": metric.category,
        "unit": metric.unit,
        "aggregation_type": metric.aggregation_type,
        "validation_rules": metric.validation_rules,
        "created_at": metric.created_at.isoformat()
    }

@router.post("/calculate/{metric_id}")
async def calculate_metric(
    metric_id: str,
    data: MetricCalculate,
    db: Session = Depends(get_db)
):
    """Calculate a metric value"""
    engine = MetricEngine(db)
    try:
        result = await engine.calculate_metric(metric_id, data.input_values)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/validate-formula")
async def validate_formula(data: FormulaValidate):
    """Validate a formula"""
    from app.services.formula_validator import FormulaValidator
    validator = FormulaValidator()
    
    is_valid, error_msg, extracted_vars = validator.validate_formula(
        data.formula,
        data.variables
    )
    
    return {
        "is_valid": is_valid,
        "error_message": error_msg,
        "extracted_variables": extracted_vars
    }

@router.get("/performance/{metric_id}")
async def get_performance(metric_id: str, db: Session = Depends(get_db)):
    """Get performance metrics"""
    engine = MetricEngine(db)
    try:
        return await engine.get_metric_performance(metric_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
