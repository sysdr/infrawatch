import re
import json
from typing import Dict, Any, List, Tuple
from jsonschema import validate, ValidationError

class RuleValidator:
    
    @staticmethod
    def validate_expression(expression: str) -> Tuple[bool, str]:
        """Validate rule expression syntax"""
        try:
            # Basic syntax validation
            if not expression.strip():
                return False, "Expression cannot be empty"
            
            # Check for valid operators
            valid_operators = ['>', '<', '>=', '<=', '==', '!=', 'and', 'or', 'not']
            
            # Check for balanced parentheses
            if expression.count('(') != expression.count(')'):
                return False, "Unbalanced parentheses in expression"
            
            # Check for valid metric names (alphanumeric + underscores)
            metric_pattern = r'[a-zA-Z_][a-zA-Z0-9_]*'
            
            # Simple validation - could be enhanced with actual parser
            if len(expression) > 1000:
                return False, "Expression too long (max 1000 characters)"
                
            return True, "Valid expression"
            
        except Exception as e:
            return False, f"Expression validation error: {str(e)}"
    
    @staticmethod 
    def validate_thresholds(thresholds: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate threshold configuration"""
        try:
            if not isinstance(thresholds, dict):
                return False, "Thresholds must be a dictionary"
            
            if not thresholds:
                return False, "At least one threshold must be defined"
            
            for key, value in thresholds.items():
                if not isinstance(key, str):
                    return False, f"Threshold key '{key}' must be a string"
                
                if not isinstance(value, (int, float)):
                    return False, f"Threshold value for '{key}' must be numeric"
            
            return True, "Valid thresholds"
            
        except Exception as e:
            return False, f"Threshold validation error: {str(e)}"
    
    @staticmethod
    def validate_rule_logic(expression: str, thresholds: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate that expression and thresholds are compatible"""
        try:
            # Extract threshold variables from expression
            threshold_vars = re.findall(r'\{(\w+)\}', expression)
            
            # Check if all threshold variables are defined
            missing_vars = [var for var in threshold_vars if var not in thresholds]
            if missing_vars:
                return False, f"Missing threshold definitions: {missing_vars}"
            
            # Check for unused thresholds
            unused_thresholds = [key for key in thresholds.keys() if key not in threshold_vars]
            if unused_thresholds:
                return False, f"Unused threshold definitions: {unused_thresholds}"
            
            return True, "Rule logic is consistent"
            
        except Exception as e:
            return False, f"Logic validation error: {str(e)}"
    
    @staticmethod
    def estimate_performance_impact(expression: str) -> Dict[str, Any]:
        """Estimate computational cost of rule evaluation"""
        complexity_score = 0
        
        # Count operators
        operators = ['and', 'or', 'not', '>', '<', '>=', '<=', '==', '!=']
        for op in operators:
            complexity_score += expression.lower().count(op)
        
        # Count function calls  
        functions = ['avg', 'sum', 'min', 'max', 'count']
        for func in functions:
            complexity_score += expression.lower().count(func) * 2
        
        # Determine impact level
        if complexity_score <= 5:
            impact = "low"
        elif complexity_score <= 15:
            impact = "medium"
        else:
            impact = "high"
        
        return {
            "complexity_score": complexity_score,
            "performance_impact": impact,
            "estimated_evaluation_time_ms": complexity_score * 10
        }
