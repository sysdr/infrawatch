import numpy as np
from scipy import stats
from typing import Dict, Optional

class TimeSeriesForecaster:
    def predict_next_value(self, values: list, hours_ahead: int = 1) -> Optional[Dict]:
        if len(values) < 10:
            return None
        
        # Simple linear regression
        x = np.arange(len(values))
        slope, intercept, _, _, _ = stats.linregress(x, values)
        
        prediction = slope * (len(values) + hours_ahead) + intercept
        std = np.std(values)
        
        return {
            'prediction': prediction,
            'confidence_lower': max(0, prediction - 1.96 * std),
            'confidence_upper': prediction + 1.96 * std
        }

forecaster = TimeSeriesForecaster()
