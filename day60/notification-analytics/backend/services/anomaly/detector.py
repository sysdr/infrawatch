import numpy as np
from typing import Dict, Optional

class AnomalyDetector:
    def __init__(self, z_threshold: float = 3.0):
        self.z_threshold = z_threshold
    
    def detect_statistical_anomaly(self, value: float, mean: float, std_dev: float) -> Optional[Dict]:
        if std_dev == 0:
            return None
        
        z_score = (value - mean) / std_dev
        
        if abs(z_score) > self.z_threshold:
            return {
                'type': 'spike' if z_score > 0 else 'drop',
                'severity': self._calculate_severity(abs(z_score)),
                'z_score': z_score,
                'expected': mean,
                'actual': value,
                'confidence': min(1.0, abs(z_score) / 10.0)
            }
        return None
    
    def _calculate_severity(self, score: float) -> str:
        if score > 5:
            return 'critical'
        elif score > 4:
            return 'high'
        elif score > 3:
            return 'medium'
        return 'low'

anomaly_detector = AnomalyDetector()
