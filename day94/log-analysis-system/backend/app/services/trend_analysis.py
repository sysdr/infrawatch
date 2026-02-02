import numpy as np
from scipy import stats
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.database import TrendData

class TrendAnalyzer:
    """
    Time-series trend analysis with decomposition, regression, and correlation analysis.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def record_metric(self, metric_name: str, value: float, 
                     time_window: str = '5min'):
        """Record a metric value for trend tracking"""
        trend = TrendData(
            metric_name=metric_name,
            time_window=time_window,
            value=value,
            extra_data={}
        )
        self.db.add(trend)
        self.db.commit()
    
    def calculate_moving_average(self, metric_name: str, 
                                window_minutes: int = 30) -> float:
        """Calculate moving average for recent data"""
        cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
        
        avg = self.db.query(func.avg(TrendData.value)).filter(
            TrendData.metric_name == metric_name,
            TrendData.timestamp >= cutoff
        ).scalar()
        
        return float(avg) if avg is not None else 0.0
    
    def detect_trend_direction(self, metric_name: str, 
                              hours: int = 24) -> str:
        """
        Detect trend direction using linear regression.
        Returns: 'up', 'down', or 'stable'
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        data = self.db.query(
            TrendData.timestamp,
            TrendData.value
        ).filter(
            TrendData.metric_name == metric_name,
            TrendData.timestamp >= cutoff
        ).order_by(TrendData.timestamp).all()
        
        if len(data) < 10:
            return 'stable'
        
        # Convert to numpy arrays
        timestamps = np.array([(d.timestamp - data[0].timestamp).total_seconds() 
                              for d in data])
        values = np.array([d.value for d in data])
        
        # Linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(timestamps, values)
        
        # Determine trend direction based on slope and significance
        if p_value > 0.05:  # Not statistically significant
            return 'stable'
        
        # Normalize slope by mean value to get percentage change
        mean_value = np.mean(values)
        if mean_value == 0:
            return 'stable'
        
        normalized_slope = (slope / mean_value) * 100
        
        if normalized_slope > 5:  # 5% increase per time unit
            return 'up'
        elif normalized_slope < -5:
            return 'down'
        else:
            return 'stable'
    
    def predict_future_value(self, metric_name: str, 
                            minutes_ahead: int = 60) -> Tuple[float, float]:
        """
        Predict future value using linear regression.
        Returns (predicted_value, confidence_interval)
        """
        cutoff = datetime.utcnow() - timedelta(hours=24)
        
        data = self.db.query(
            TrendData.timestamp,
            TrendData.value
        ).filter(
            TrendData.metric_name == metric_name,
            TrendData.timestamp >= cutoff
        ).order_by(TrendData.timestamp).all()
        
        if len(data) < 10:
            return 0.0, 0.0
        
        timestamps = np.array([(d.timestamp - data[0].timestamp).total_seconds() 
                              for d in data])
        values = np.array([d.value for d in data])
        
        slope, intercept, r_value, p_value, std_err = stats.linregress(timestamps, values)
        
        # Predict at future time
        future_timestamp = timestamps[-1] + (minutes_ahead * 60)
        predicted_value = slope * future_timestamp + intercept
        
        # Calculate confidence interval (95%)
        confidence = 1.96 * std_err * np.sqrt(1 + 1/len(timestamps))
        
        return float(predicted_value), float(confidence)
    
    def calculate_correlation(self, metric1: str, metric2: str,
                             hours: int = 24) -> float:
        """
        Calculate correlation coefficient between two metrics.
        Returns correlation value between -1 and 1.
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        # Get synchronized time points
        data1 = self.db.query(TrendData).filter(
            TrendData.metric_name == metric1,
            TrendData.timestamp >= cutoff
        ).order_by(TrendData.timestamp).all()
        
        data2 = self.db.query(TrendData).filter(
            TrendData.metric_name == metric2,
            TrendData.timestamp >= cutoff
        ).order_by(TrendData.timestamp).all()
        
        if len(data1) < 10 or len(data2) < 10:
            return 0.0
        
        # Align timestamps (simplified - assumes regular intervals)
        values1 = np.array([d.value for d in data1[:min(len(data1), len(data2))]])
        values2 = np.array([d.value for d in data2[:min(len(data1), len(data2))]])
        
        if len(values1) < 2 or len(values2) < 2:
            return 0.0
        
        correlation, _ = stats.pearsonr(values1, values2)
        return float(correlation)
    
    def get_trend_summary(self, hours: int = 24) -> List[Dict]:
        """Get trend summary for all tracked metrics"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        # Get unique metrics
        metrics = self.db.query(TrendData.metric_name).filter(
            TrendData.timestamp >= cutoff
        ).distinct().all()
        
        summary = []
        for (metric_name,) in metrics:
            direction = self.detect_trend_direction(metric_name, hours=hours)
            moving_avg = self.calculate_moving_average(metric_name, window_minutes=30)
            predicted, confidence = self.predict_future_value(metric_name, minutes_ahead=60)
            
            summary.append({
                'metric_name': metric_name,
                'trend_direction': direction,
                'moving_average': moving_avg,
                'predicted_value_1h': predicted,
                'confidence_interval': confidence
            })
        
        return summary
