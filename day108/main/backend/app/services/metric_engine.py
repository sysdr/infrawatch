from typing import Dict, List, Optional
import time
from datetime import datetime
import asyncio
from sqlalchemy.orm import Session
from app.models.metric import MetricDefinition, MetricCalculation, PerformanceMetric
from sqlalchemy import func
from app.services.formula_validator import FormulaValidator
import json

class MetricEngine:
    """Core engine for metric calculations and management"""
    
    def __init__(self, db: Session):
        self.db = db
        self.validator = FormulaValidator()
        self.cache = {}  # Simple in-memory cache
    
    async def create_metric(self, metric_data: Dict) -> MetricDefinition:
        """Create a new metric definition"""
        # Validate formula
        is_valid, error_msg, extracted_vars = self.validator.validate_formula(
            metric_data['formula'],
            metric_data['variables']
        )
        
        if not is_valid:
            raise ValueError(f"Invalid formula: {error_msg}")
        
        # Create metric definition
        metric = MetricDefinition(
            name=metric_data['name'],
            display_name=metric_data.get('display_name', metric_data['name']),
            description=metric_data.get('description', ''),
            formula=metric_data['formula'],
            variables=metric_data['variables'],
            category=metric_data.get('category', 'custom'),
            unit=metric_data.get('unit', ''),
            aggregation_type=metric_data.get('aggregation_type', 'sum'),
            validation_rules=metric_data.get('validation_rules', {}),
            created_by=metric_data.get('created_by', 'system')
        )
        
        self.db.add(metric)
        self.db.commit()
        self.db.refresh(metric)
        
        # Initialize performance tracking
        perf_metric = PerformanceMetric(
            metric_id=metric.id,
            avg_execution_time=0.0,
            max_execution_time=0.0,
            min_execution_time=0.0
        )
        self.db.add(perf_metric)
        self.db.commit()
        
        return metric
    
    async def calculate_metric(self, metric_id: str, input_values: Dict[str, float]) -> Dict:
        """Calculate metric value with performance tracking"""
        start_time = time.time()
        
        # Get metric definition
        metric = self.db.query(MetricDefinition).filter_by(id=metric_id).first()
        if not metric:
            raise ValueError(f"Metric {metric_id} not found")
        
        try:
            # Validate input values
            self._validate_inputs(metric, input_values)
            
            # Calculate value
            calculated_value = self.validator.evaluate_formula(metric.formula, input_values)
            
            execution_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Store calculation record
            calculation = MetricCalculation(
                metric_id=metric_id,
                input_values=input_values,
                calculated_value=calculated_value,
                execution_time_ms=execution_time,
                status='success'
            )
            self.db.add(calculation)
            
            # Update performance metrics
            await self._update_performance_metrics(metric_id, execution_time, True)
            
            self.db.commit()
            
            return {
                'metric_id': metric_id,
                'metric_name': metric.name,
                'calculated_value': calculated_value,
                'unit': metric.unit,
                'execution_time_ms': execution_time,
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'success'
            }
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            
            # Store failed calculation
            calculation = MetricCalculation(
                metric_id=metric_id,
                input_values=input_values,
                execution_time_ms=execution_time,
                status='failed',
                error_message=str(e)
            )
            self.db.add(calculation)
            
            await self._update_performance_metrics(metric_id, execution_time, False)
            self.db.commit()
            
            raise ValueError(f"Calculation failed: {str(e)}")
    
    def _validate_inputs(self, metric: MetricDefinition, input_values: Dict[str, float]):
        """Validate input values against metric requirements"""
        # Check all required variables are provided
        required_vars = set(metric.variables)
        provided_vars = set(input_values.keys())
        
        missing_vars = required_vars - provided_vars
        if missing_vars:
            raise ValueError(f"Missing required variables: {', '.join(missing_vars)}")
        
        # Apply validation rules
        validation_rules = metric.validation_rules or {}
        for var, value in input_values.items():
            if var in validation_rules:
                rules = validation_rules[var]
                
                if 'min' in rules and value < rules['min']:
                    raise ValueError(f"{var} must be >= {rules['min']}")
                
                if 'max' in rules and value > rules['max']:
                    raise ValueError(f"{var} must be <= {rules['max']}")
                
                if 'type' in rules:
                    expected_type = rules['type']
                    if expected_type == 'integer' and not isinstance(value, int):
                        raise ValueError(f"{var} must be an integer")
    
    async def _update_performance_metrics(self, metric_id: str, execution_time: float, success: bool):
        """Update performance tracking metrics"""
        perf = self.db.query(PerformanceMetric).filter_by(metric_id=metric_id).first()
        
        if perf:
            perf.total_executions += 1
            if not success:
                perf.failed_executions += 1
            
            # Update execution time stats
            if success:
                if perf.total_executions == 1:
                    perf.avg_execution_time = execution_time
                    perf.min_execution_time = execution_time
                    perf.max_execution_time = execution_time
                else:
                    perf.avg_execution_time = (
                        (perf.avg_execution_time * (perf.total_executions - 1) + execution_time) /
                        perf.total_executions
                    )
                    perf.min_execution_time = min(perf.min_execution_time, execution_time)
                    perf.max_execution_time = max(perf.max_execution_time, execution_time)
            
            perf.last_updated = datetime.utcnow()
            self.db.commit()
    
    async def get_metric_performance(self, metric_id: str) -> Dict:
        """Get performance statistics for a metric (computed from actual calculation records)"""
        perf = self.db.query(PerformanceMetric).filter_by(metric_id=metric_id).first()
        metric = self.db.query(MetricDefinition).filter_by(id=metric_id).first()
        
        if not perf or not metric:
            raise ValueError(f"Metric {metric_id} not found")
        
        # Compute real-time stats from MetricCalculation (source of truth)
        total_executions = self.db.query(func.count(MetricCalculation.id)).filter(
            MetricCalculation.metric_id == metric_id
        ).scalar() or 0
        success_count = self.db.query(func.count(MetricCalculation.id)).filter(
            MetricCalculation.metric_id == metric_id,
            MetricCalculation.status == 'success'
        ).scalar() or 0
        failed_executions = total_executions - success_count
        success_rate = (success_count / total_executions * 100) if total_executions > 0 else 0
        
        return {
            'metric_id': metric_id,
            'metric_name': metric.name,
            'total_executions': total_executions,
            'failed_executions': failed_executions,
            'success_rate': round(success_rate, 2),
            'avg_execution_time_ms': round(perf.avg_execution_time or 0, 2),
            'min_execution_time_ms': round(perf.min_execution_time or 0, 2),
            'max_execution_time_ms': round(perf.max_execution_time or 0, 2),
            'last_updated': perf.last_updated.isoformat() if perf.last_updated else None
        }
