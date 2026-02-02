import numpy as np
from sklearn.ensemble import IsolationForest
from scipy import stats
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.database import Anomaly, TrendData
import json

class AnomalyDetector:
    """
    Multi-algorithm anomaly detection system using:
    - Z-score analysis for sudden spikes
    - Moving average comparison for trend changes
    - Isolation Forest for multivariate anomalies
    """
    
    def __init__(self, db: Session, threshold: float = 3.0):
        self.db = db
        self.threshold = threshold
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
    
    def calculate_baseline(self, metric_name: str, hours: int = 24) -> Tuple[float, float]:
        """Calculate baseline mean and standard deviation for a metric (SQLite-compatible)"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        values = [
            row[0] for row in self.db.query(TrendData.value).filter(
                TrendData.metric_name == metric_name,
                TrendData.timestamp >= cutoff
            ).all()
        ]
        
        if not values:
            return 0.0, 0.1
        arr = np.array(values, dtype=float)
        mean = float(np.mean(arr))
        stddev = float(np.std(arr)) if len(arr) > 1 else 0.1
        return mean, (stddev if stddev > 0 else 0.1)
    
    def detect_zscore_anomaly(self, metric_name: str, current_value: float,
                             source: str) -> Optional[Anomaly]:
        """
        Detect anomalies using Z-score analysis.
        Flags values that are > threshold standard deviations from mean.
        """
        mean, stddev = self.calculate_baseline(metric_name)
        
        if stddev == 0:
            stddev = 0.1  # Avoid division by zero
        
        z_score = abs((current_value - mean) / stddev)
        
        if z_score > self.threshold:
            anomaly_type = 'spike' if current_value > mean else 'drop'
            severity = 'critical' if z_score > 5 else 'high' if z_score > 4 else 'medium'
            
            anomaly = Anomaly(
                metric_name=metric_name,
                metric_value=current_value,
                baseline_mean=mean,
                baseline_stddev=stddev,
                z_score=z_score,
                anomaly_type=anomaly_type,
                severity=severity,
                source=source,
                extra_data={
                    'detection_method': 'z_score',
                    'threshold': self.threshold
                }
            )
            
            self.db.add(anomaly)
            self.db.commit()
            self.db.refresh(anomaly)
            
            return anomaly
        
        return None
    
    def detect_moving_average_anomaly(self, metric_name: str, 
                                     short_window: int = 5,
                                     long_window: int = 60) -> Optional[Anomaly]:
        """
        Detect anomalies by comparing short-term vs long-term moving averages.
        Catches gradual degradation that Z-score might miss.
        """
        now = datetime.utcnow()
        short_cutoff = now - timedelta(minutes=short_window)
        long_cutoff = now - timedelta(minutes=long_window)
        
        # Short-term average (last 5 minutes)
        short_avg = self.db.query(func.avg(TrendData.value)).filter(
            TrendData.metric_name == metric_name,
            TrendData.timestamp >= short_cutoff
        ).scalar()
        
        # Long-term average (last hour)
        long_avg = self.db.query(func.avg(TrendData.value)).filter(
            TrendData.metric_name == metric_name,
            TrendData.timestamp >= long_cutoff
        ).scalar()
        
        if short_avg is None or long_avg is None or long_avg == 0:
            return None
        
        # Calculate percentage deviation
        deviation = abs((short_avg - long_avg) / long_avg) * 100
        
        if deviation > 50:  # 50% deviation threshold
            anomaly_type = 'trend_change'
            severity = 'high' if deviation > 100 else 'medium'
            
            anomaly = Anomaly(
                metric_name=metric_name,
                metric_value=float(short_avg),
                baseline_mean=float(long_avg),
                baseline_stddev=0.0,
                z_score=deviation / 10,  # Normalized z-score equivalent
                anomaly_type=anomaly_type,
                severity=severity,
                source='moving_average',
                extra_data={
                    'detection_method': 'moving_average',
                    'short_window_minutes': short_window,
                    'long_window_minutes': long_window,
                    'deviation_percent': deviation
                }
            )
            
            self.db.add(anomaly)
            self.db.commit()
            self.db.refresh(anomaly)
            
            return anomaly
        
        return None
    
    def detect_multivariate_anomalies(self, metrics: Dict[str, float],
                                     source: str) -> List[Anomaly]:
        """
        Detect anomalies in high-dimensional data using Isolation Forest.
        Identifies unusual combinations of metrics.
        """
        if len(metrics) < 2:
            return []
        
        # Prepare data matrix
        metric_names = sorted(metrics.keys())
        current_values = np.array([[metrics[k] for k in metric_names]])
        
        # Get historical data for training
        historical_data = []
        cutoff = datetime.utcnow() - timedelta(hours=24)
        
        for metric_name in metric_names:
            values = self.db.query(TrendData.value).filter(
                TrendData.metric_name == metric_name,
                TrendData.timestamp >= cutoff
            ).order_by(TrendData.timestamp.desc()).limit(1000).all()
            
            historical_data.append([v[0] for v in values])
        
        if not historical_data or len(historical_data[0]) < 10:
            return []
        
        # Transpose to get samples x features
        X_train = np.array(historical_data).T
        
        # Train and predict
        try:
            self.isolation_forest.fit(X_train)
            prediction = self.isolation_forest.predict(current_values)
            
            if prediction[0] == -1:  # Anomaly detected
                anomalies = []
                for metric_name, value in metrics.items():
                    anomaly = Anomaly(
                        metric_name=metric_name,
                        metric_value=value,
                        baseline_mean=0.0,
                        baseline_stddev=0.0,
                        z_score=0.0,
                        anomaly_type='multivariate',
                        severity='medium',
                        source=source,
                        extra_data={
                            'detection_method': 'isolation_forest',
                            'all_metrics': metrics
                        }
                    )
                    anomalies.append(anomaly)
                    self.db.add(anomaly)
                
                self.db.commit()
                return anomalies
        except Exception as e:
            print(f"Isolation Forest error: {e}")
        
        return []
    
    def get_recent_anomalies(self, hours: int = 24, 
                            resolved: bool = False) -> List[Dict]:
        """Get recent anomalies for dashboard display"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        query = self.db.query(Anomaly).filter(
            Anomaly.timestamp >= cutoff,
            Anomaly.resolved == resolved
        ).order_by(Anomaly.timestamp.desc()).limit(100)
        
        return [
            {
                'id': a.id,
                'timestamp': a.timestamp.isoformat(),
                'metric_name': a.metric_name,
                'metric_value': a.metric_value,
                'z_score': a.z_score,
                'anomaly_type': a.anomaly_type,
                'severity': a.severity,
                'source': a.source
            }
            for a in query.all()
        ]
