import pytest
import asyncio
from src.validation.metric_validator import MetricValidator

@pytest.mark.asyncio
async def test_valid_cpu_metric():
    validator = MetricValidator()
    
    valid_metric = {
        "name": "cpu_usage",
        "value": 75.5,
        "unit": "%"
    }
    
    result = await validator.validate_metric(valid_metric)
    assert result is True

@pytest.mark.asyncio
async def test_invalid_metric_range():
    validator = MetricValidator()
    
    invalid_metric = {
        "name": "cpu_usage",
        "value": 150.0,  # Invalid range
        "unit": "%"
    }
    
    result = await validator.validate_metric(invalid_metric)
    assert result is False

@pytest.mark.asyncio
async def test_missing_required_field():
    validator = MetricValidator()
    
    invalid_metric = {
        "name": "cpu_usage",
        # Missing value and unit
    }
    
    result = await validator.validate_metric(invalid_metric)
    assert result is False
