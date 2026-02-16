import pytest
from app.services.formula_validator import FormulaValidator
from app.services.metric_engine import MetricEngine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.metric import Base, MetricDefinition

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_formula_validation():
    validator = FormulaValidator()
    
    # Valid formula
    is_valid, error, vars = validator.validate_formula("revenue - cost", ["revenue", "cost"])
    assert is_valid == True
    
    # Invalid formula
    is_valid, error, vars = validator.validate_formula("revenue - undefined_var", ["revenue"])
    assert is_valid == False

def test_formula_evaluation():
    validator = FormulaValidator()
    
    result = validator.evaluate_formula("revenue - cost", {"revenue": 1000, "cost": 600})
    assert result == 400
    
    result = validator.evaluate_formula("(revenue / cost) * 100", {"revenue": 1000, "cost": 500})
    assert result == 200

@pytest.mark.asyncio
async def test_metric_creation(db_session):
    engine = MetricEngine(db_session)
    
    metric_data = {
        "name": "profit_margin",
        "display_name": "Profit Margin",
        "formula": "(revenue - cost) / revenue * 100",
        "variables": ["revenue", "cost"],
        "unit": "%",
        "category": "financial"
    }
    
    metric = await engine.create_metric(metric_data)
    assert metric.name == "profit_margin"
    assert metric.formula == "(revenue - cost) / revenue * 100"

@pytest.mark.asyncio
async def test_metric_calculation(db_session):
    engine = MetricEngine(db_session)
    
    metric_data = {
        "name": "roi",
        "display_name": "ROI",
        "formula": "(gain - cost) / cost * 100",
        "variables": ["gain", "cost"],
        "unit": "%"
    }
    
    metric = await engine.create_metric(metric_data)
    
    result = await engine.calculate_metric(
        metric.id,
        {"gain": 1500, "cost": 1000}
    )
    
    assert result["status"] == "success"
    assert result["calculated_value"] == 50.0
