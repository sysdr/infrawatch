import time
import json
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.database import RuleTest, AlertRule
from app.models.rules import RuleTestRequest
from app.validators.rule_validator import RuleValidator

class RuleTestingService:
    
    def __init__(self, db: Session):
        self.db = db
        self.validator = RuleValidator()
    
    def test_rule(self, test_request: RuleTestRequest) -> Dict[str, Any]:
        """Test rule against provided data"""
        start_time = time.time()
        
        # Get rule configuration
        if test_request.rule_id:
            rule = self.db.query(AlertRule).filter(AlertRule.id == test_request.rule_id).first()
            if not rule:
                raise ValueError(f"Rule with ID {test_request.rule_id} not found")
            rule_config = {
                'expression': rule.expression,
                'thresholds': rule.thresholds,
                'severity': rule.severity
            }
        elif test_request.rule_config:
            rule_config = {
                'expression': test_request.rule_config.expression,
                'thresholds': test_request.rule_config.thresholds,
                'severity': test_request.rule_config.severity
            }
        else:
            raise ValueError("Either rule_id or rule_config must be provided")
        
        # Run tests
        test_results = []
        passed_count = 0
        
        for i, (test_data, expected) in enumerate(zip(test_request.test_data, test_request.expected_results)):
            try:
                actual_result = self._evaluate_rule(rule_config, test_data)
                passed = actual_result == expected
                if passed:
                    passed_count += 1
                
                test_results.append({
                    "test_case": i + 1,
                    "test_data": test_data,
                    "expected": expected,
                    "actual": actual_result,
                    "passed": passed
                })
                
            except Exception as e:
                test_results.append({
                    "test_case": i + 1,
                    "test_data": test_data,
                    "expected": expected,
                    "actual": None,
                    "passed": False,
                    "error": str(e)
                })
        
        execution_time = (time.time() - start_time) * 1000
        
        # Save test results if rule_id provided
        if test_request.rule_id:
            db_test = RuleTest(
                rule_id=test_request.rule_id,
                test_data=test_request.test_data,
                expected_result=all(test_request.expected_results),
                actual_result=passed_count == len(test_request.expected_results),
                test_status="completed"
            )
            self.db.add(db_test)
            self.db.commit()
            self.db.refresh(db_test)
            test_id = db_test.id
        else:
            test_id = None
        
        return {
            "test_id": test_id,
            "rule_id": test_request.rule_id,
            "total_tests": len(test_request.test_data),
            "passed_tests": passed_count,
            "success_rate": passed_count / len(test_request.test_data) * 100,
            "execution_time_ms": execution_time,
            "results": test_results,
            "overall_passed": passed_count == len(test_request.test_data)
        }
    
    def _evaluate_rule(self, rule_config: Dict[str, Any], test_data: Dict[str, Any]) -> bool:
        """Evaluate rule against test data (simplified implementation)"""
        expression = rule_config['expression']
        thresholds = rule_config['thresholds']
        
        # Replace threshold placeholders
        for key, value in thresholds.items():
            expression = expression.replace(f'{{{key}}}', str(value))
        
        # Simple evaluation for demo purposes
        # In production, this would use a proper expression evaluator
        try:
            # Extract metric values from test data
            for metric, value in test_data.items():
                if metric in expression:
                    expression = expression.replace(metric, str(value))
            
            # Basic evaluation for common patterns
            if 'avg(' in expression:
                # Extract metric name and evaluate
                import re
                avg_match = re.search(r'avg\(([^)]+)\)', expression)
                if avg_match:
                    metric_name = avg_match.group(1)
                    if metric_name in test_data:
                        metric_value = test_data[metric_name]
                        expression = expression.replace(avg_match.group(0), str(metric_value))
            
            # Evaluate simple comparison expressions
            if ' > ' in expression:
                parts = expression.split(' > ')
                if len(parts) == 2:
                    try:
                        left = float(parts[0].strip())
                        right = float(parts[1].strip())
                        return left > right
                    except ValueError:
                        pass
            
            # Default: return False for unsupported expressions
            return False
            
        except Exception:
            return False
    
    def get_test_history(self, rule_id: int) -> List[RuleTest]:
        """Get test history for a rule"""
        return self.db.query(RuleTest).filter(RuleTest.rule_id == rule_id).all()
    
    def validate_rule_syntax(self, expression: str, thresholds: Dict[str, Any]) -> Dict[str, Any]:
        """Validate rule syntax and return detailed feedback"""
        results = {}
        
        # Expression validation
        is_valid, message = self.validator.validate_expression(expression)
        results['expression_valid'] = is_valid
        results['expression_message'] = message
        
        # Threshold validation
        is_valid, message = self.validator.validate_thresholds(thresholds)
        results['thresholds_valid'] = is_valid
        results['thresholds_message'] = message
        
        # Logic validation
        is_valid, message = self.validator.validate_rule_logic(expression, thresholds)
        results['logic_valid'] = is_valid
        results['logic_message'] = message
        
        # Performance estimation
        results['performance_impact'] = self.validator.estimate_performance_impact(expression)
        
        results['overall_valid'] = all([
            results['expression_valid'],
            results['thresholds_valid'], 
            results['logic_valid']
        ])
        
        return results
