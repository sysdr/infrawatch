from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from app.models.database import get_db
from app.models.rules import RuleTestRequest
from app.services.testing_service import RuleTestingService

router = APIRouter()

@router.post("/rule")
async def test_rule(test_request: RuleTestRequest, db: Session = Depends(get_db)):
    """Test a rule against provided data"""
    try:
        service = RuleTestingService(db)
        results = service.test_rule(test_request)
        return results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test execution failed: {str(e)}")

@router.get("/history/{rule_id}")
async def get_test_history(rule_id: int, db: Session = Depends(get_db)):
    """Get test history for a rule"""
    service = RuleTestingService(db)
    history = service.get_test_history(rule_id)
    return {"rule_id": rule_id, "test_history": history}

@router.post("/validate")
async def validate_rule_syntax(
    expression: str,
    thresholds: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Validate rule syntax and logic"""
    service = RuleTestingService(db)
    results = service.validate_rule_syntax(expression, thresholds)
    return results

@router.post("/example-data")
async def get_example_test_data():
    """Get example test data for rule testing"""
    return {
        "cpu_utilization_test": {
            "test_data": [
                {"cpu_usage_percent": 45.2},
                {"cpu_usage_percent": 89.7},
                {"cpu_usage_percent": 92.1}
            ],
            "expected_results": [False, True, True],
            "rule_expression": "avg(cpu_usage_percent) > {threshold}",
            "thresholds": {"threshold": 85}
        },
        "memory_utilization_test": {
            "test_data": [
                {"memory_usage_percent": 65.0},
                {"memory_usage_percent": 91.5},
                {"memory_usage_percent": 95.2}
            ],
            "expected_results": [False, True, True],
            "rule_expression": "avg(memory_usage_percent) > {threshold}",
            "thresholds": {"threshold": 90}
        },
        "api_response_time_test": {
            "test_data": [
                {"response_time_ms": 1200},
                {"response_time_ms": 2500},
                {"response_time_ms": 3100}
            ],
            "expected_results": [False, True, True],
            "rule_expression": "avg(response_time_ms) > {threshold}",
            "thresholds": {"threshold": 2000}
        }
    }
