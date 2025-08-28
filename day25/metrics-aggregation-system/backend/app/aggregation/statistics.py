import statistics
import numpy as np
from typing import List, Dict, Any, Optional
import math

class StatisticalCalculator:
    """Advanced statistical calculations for metrics"""
    
    def percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile value"""
        if not values:
            return 0.0
        return float(np.percentile(values, percentile))
    
    def standard_deviation(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if len(values) < 2:
            return 0.0
        return float(statistics.stdev(values))
    
    def variance(self, values: List[float]) -> float:
        """Calculate variance"""
        if len(values) < 2:
            return 0.0
        return float(statistics.variance(values))
    
    def rate_of_change(self, values: List[float]) -> float:
        """Calculate rate of change between first and last values"""
        if len(values) < 2:
            return 0.0
        
        first, last = values[0], values[-1]
        if first == 0:
            return 0.0
        
        return ((last - first) / first) * 100
    
    def moving_average(self, values: List[float], window_size: int = 5) -> List[float]:
        """Calculate moving average"""
        if len(values) < window_size:
            return values
        
        moving_averages = []
        for i in range(len(values) - window_size + 1):
            window = values[i:i + window_size]
            moving_averages.append(sum(window) / window_size)
        
        return moving_averages
    
    def detect_anomalies(self, values: List[float], threshold_std: float = 2.0) -> List[int]:
        """Detect anomalies using standard deviation threshold"""
        if len(values) < 3:
            return []
        
        mean_val = statistics.mean(values)
        std_val = self.standard_deviation(values)
        
        anomalies = []
        for i, value in enumerate(values):
            if abs(value - mean_val) > threshold_std * std_val:
                anomalies.append(i)
        
        return anomalies
    
    def correlation(self, x_values: List[float], y_values: List[float]) -> float:
        """Calculate correlation coefficient between two series"""
        if len(x_values) != len(y_values) or len(x_values) < 2:
            return 0.0
        
        try:
            return float(np.corrcoef(x_values, y_values)[0, 1])
        except:
            return 0.0
    
    def linear_regression_slope(self, values: List[float]) -> float:
        """Calculate linear regression slope for trend analysis"""
        if len(values) < 2:
            return 0.0
        
        x = list(range(len(values)))
        y = values
        
        n = len(values)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        denominator = n * sum_x2 - sum_x ** 2
        if denominator == 0:
            return 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        return float(slope)
    
    def seasonality_detection(self, values: List[float], period: int = 24) -> Dict[str, Any]:
        """Basic seasonality detection"""
        if len(values) < period * 2:
            return {"has_seasonality": False, "confidence": 0.0}
        
        # Simple autocorrelation at the specified period
        n = len(values)
        if period >= n:
            return {"has_seasonality": False, "confidence": 0.0}
        
        # Calculate autocorrelation at the period lag
        mean_val = statistics.mean(values)
        
        # Autocorrelation calculation
        numerator = sum((values[i] - mean_val) * (values[i - period] - mean_val) 
                       for i in range(period, n))
        denominator = sum((values[i] - mean_val) ** 2 for i in range(n))
        
        if denominator == 0:
            autocorr = 0
        else:
            autocorr = numerator / denominator
        
        # Simple threshold for seasonality detection
        has_seasonality = abs(autocorr) > 0.3
        confidence = min(abs(autocorr), 1.0)
        
        return {
            "has_seasonality": has_seasonality,
            "confidence": confidence,
            "autocorrelation": autocorr,
            "period": period
        }
