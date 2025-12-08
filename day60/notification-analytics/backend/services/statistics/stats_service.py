import numpy as np
from typing import Dict, Optional
from datetime import datetime, timedelta

class StatisticsService:
    def calculate_stats(self, values: list) -> Dict:
        if not values:
            return None
        
        return {
            'mean': float(np.mean(values)),
            'median': float(np.median(values)),
            'std_dev': float(np.std(values)),
            'p50': float(np.percentile(values, 50)),
            'p95': float(np.percentile(values, 95)),
            'p99': float(np.percentile(values, 99)),
            'min': float(np.min(values)),
            'max': float(np.max(values)),
            'count': len(values),
            'variance': float(np.var(values))
        }

stats_service = StatisticsService()
