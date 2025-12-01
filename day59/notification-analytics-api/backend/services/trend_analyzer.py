from typing import List, Dict, Optional
from datetime import datetime
import numpy as np
from dataclasses import dataclass

@dataclass
class TrendAnalysis:
    """Results of trend analysis"""
    moving_average: List[float]
    anomalies: List[Dict]
    percent_change: float
    direction: str
    trend: str  # 'increasing', 'decreasing', 'stable'

class TrendAnalyzer:
    """Analyze trends in time-series data"""
    
    @staticmethod
    def moving_average(values: List[float], window: int = 7) -> List[float]:
        """Calculate moving average"""
        if len(values) < window:
            return values
        
        ma = []
        for i in range(len(values)):
            if i < window - 1:
                ma.append(np.mean(values[:i+1]))
            else:
                ma.append(np.mean(values[i-window+1:i+1]))
        return ma
    
    @staticmethod
    def detect_anomalies(data: List[Dict], threshold: float = 2.0) -> List[Dict]:
        """Detect anomalies using standard deviation"""
        # Convert to float to handle Decimal types from database
        values = [float(d['value']) for d in data]
        
        if len(values) < 3:
            return []
        
        mean = np.mean(values)
        std = np.std(values)
        
        if std == 0:
            return []
        
        anomalies = []
        for i, point in enumerate(data):
            # Convert to float to handle Decimal types from database
            point_value = float(point['value'])
            z_score = abs((point_value - mean) / std)
            if z_score > threshold:
                anomalies.append({
                    'index': i,
                    'time': point.get('time'),
                    'value': point_value,
                    'expected': mean,
                    'deviation': z_score
                })
        
        return anomalies
    
    @staticmethod
    def calculate_percent_change(values: List[float]) -> float:
        """Calculate percentage change from first to last value"""
        if len(values) < 2 or values[0] == 0:
            return 0.0
        
        return ((values[-1] - values[0]) / values[0]) * 100
    
    @staticmethod
    def determine_trend(values: List[float]) -> str:
        """Determine overall trend direction"""
        if len(values) < 2:
            return 'stable'
        
        # Use linear regression slope
        x = np.arange(len(values))
        # Convert to float to handle Decimal types from database
        y = np.array([float(v) for v in values])
        
        slope = np.polyfit(x, y, 1)[0]
        
        # Threshold for "stable" is 1% change per period
        avg_value = np.mean(values)
        if abs(slope) < avg_value * 0.01:
            return 'stable'
        elif slope > 0:
            return 'increasing'
        else:
            return 'decreasing'
    
    def analyze_trends(self, data: List[Dict], window: int = 7) -> TrendAnalysis:
        """Perform comprehensive trend analysis"""
        # Convert to float to handle Decimal types from database
        values = [float(d['value']) for d in data]
        
        if len(values) == 0:
            return TrendAnalysis(
                moving_average=[],
                anomalies=[],
                percent_change=0.0,
                direction='stable',
                trend='stable'
            )
        
        ma = self.moving_average(values, window)
        anomalies = self.detect_anomalies(data)
        pct_change = self.calculate_percent_change(values)
        trend = self.determine_trend(values)
        
        direction = 'up' if pct_change > 0 else 'down' if pct_change < 0 else 'stable'
        
        return TrendAnalysis(
            moving_average=ma,
            anomalies=anomalies,
            percent_change=pct_change,
            direction=direction,
            trend=trend
        )
