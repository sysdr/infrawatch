import time
from typing import Dict, Any, List
import structlog

logger = structlog.get_logger()

class MetricValidator:
    def __init__(self):
        self.validation_rules = {
            "cpu": {
                "required_fields": ["name", "value", "unit"],
                "value_range": (0, 100),
                "unit": "%"
            },
            "memory": {
                "required_fields": ["name", "value", "unit"],
                "value_range": (0, 100),
                "unit": "%"
            },
            "disk": {
                "required_fields": ["name", "value", "unit", "device"],
                "value_range": (0, float('inf')),
                "unit": ["GB", "%"]  # Allow both GB and percentage
            },
            "network": {
                "required_fields": ["name", "value", "unit", "interface"],
                "value_range": (0, float('inf')),
                "unit": ["MB/s", "MB", "KB"]  # Allow various network units
            },
            "app": {
                "required_fields": ["name", "value", "unit"],
                "value_range": (0, float('inf')),
                "unit": None  # Flexible units for app metrics
            },
            "database": {
                "required_fields": ["name", "value", "unit"],
                "value_range": (0, float('inf')),
                "unit": None  # Flexible units for database metrics
            }
        }
        
        self.validation_stats = {
            "total_validated": 0,
            "valid_metrics": 0,
            "invalid_metrics": 0,
            "validation_errors": []
        }

    async def validate_metric(self, metric_data: Dict[str, Any]) -> bool:
        """Validate metric data against defined rules"""
        self.validation_stats["total_validated"] += 1
        
        try:
            # Basic structure validation
            if not isinstance(metric_data, dict):
                self._record_error("Metric data must be a dictionary")
                return False

            metric_name = metric_data.get("name", "").lower()
            metric_type = self._extract_metric_type(metric_name)
            
            if metric_type not in self.validation_rules:
                self._record_error(f"Unknown metric type: {metric_type}")
                return False

            rules = self.validation_rules[metric_type]
            
            # Check required fields
            for field in rules["required_fields"]:
                if field not in metric_data:
                    self._record_error(f"Missing required field: {field}")
                    return False

            # Validate value range
            value = metric_data.get("value")
            if not isinstance(value, (int, float)):
                self._record_error(f"Value must be numeric, got: {type(value)}")
                return False

            min_val, max_val = rules["value_range"]
            if not (min_val <= value <= max_val):
                self._record_error(f"Value {value} outside valid range [{min_val}, {max_val}]")
                return False

            # Validate unit
            expected_unit = rules.get("unit")
            if expected_unit:
                if isinstance(expected_unit, list):
                    # Handle list of allowed units
                    if metric_data.get("unit") not in expected_unit:
                        self._record_error(f"Expected unit to be one of {expected_unit}, got '{metric_data.get('unit')}'")
                        return False
                else:
                    # Handle single expected unit
                    if metric_data.get("unit") != expected_unit:
                        self._record_error(f"Expected unit '{expected_unit}', got '{metric_data.get('unit')}'")
                        return False
            elif expected_unit is None:
                # For flexible units (app, database), just ensure unit is present
                if "unit" not in metric_data:
                    self._record_error("Unit field is required")
                    return False

            # Timestamp validation
            if "timestamp" in metric_data:
                timestamp = metric_data["timestamp"]
                current_time = time.time()
                
                # Allow timestamps within 1 hour of current time
                if abs(timestamp - current_time) > 3600:
                    self._record_error("Timestamp too far from current time")
                    return False

            self.validation_stats["valid_metrics"] += 1
            return True
            
        except Exception as e:
            self._record_error(f"Validation exception: {str(e)}")
            return False

    def _extract_metric_type(self, metric_name: str) -> str:
        """Extract metric type from metric name"""
        if "cpu" in metric_name:
            return "cpu"
        elif "memory" in metric_name or "ram" in metric_name:
            return "memory"
        elif "disk" in metric_name or "storage" in metric_name:
            return "disk"
        elif "network" in metric_name or "net" in metric_name:
            return "network"
        elif "app" in metric_name or "response" in metric_name or "request" in metric_name or "error" in metric_name:
            return "app"
        elif "database" in metric_name or "db" in metric_name or "connection" in metric_name:
            return "database"
        else:
            return "unknown"

    def _record_error(self, error_message: str):
        """Record validation error"""
        self.validation_stats["invalid_metrics"] += 1
        self.validation_stats["validation_errors"].append({
            "timestamp": time.time(),
            "error": error_message
        })
        
        # Keep only last 100 errors
        if len(self.validation_stats["validation_errors"]) > 100:
            self.validation_stats["validation_errors"] = self.validation_stats["validation_errors"][-100:]
        
        logger.warning(f"Validation error: {error_message}")

    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics"""
        return self.validation_stats.copy()

    def add_validation_rule(self, metric_type: str, rules: Dict[str, Any]):
        """Add custom validation rule"""
        self.validation_rules[metric_type] = rules
        logger.info(f"Added validation rules for metric type: {metric_type}")
