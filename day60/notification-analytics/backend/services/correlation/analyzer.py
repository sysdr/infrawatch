import numpy as np
from scipy.stats import pearsonr
from typing import List, Dict, Optional

class CorrelationAnalyzer:
    def calculate_correlation(self, values_a: List[float], values_b: List[float]) -> Optional[float]:
        if len(values_a) < 3 or len(values_b) < 3:
            return None
        
        min_len = min(len(values_a), len(values_b))
        values_a = values_a[:min_len]
        values_b = values_b[:min_len]
        
        correlation, p_value = pearsonr(values_a, values_b)
        
        if p_value > 0.05:
            return None
        
        return correlation

correlation_analyzer = CorrelationAnalyzer()
