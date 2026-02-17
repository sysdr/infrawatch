import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.correlation_engine import CorrelationEngine
from services.root_cause_analyzer import RootCauseAnalyzer
from services.impact_assessor import ImpactAssessor
import pandas as pd
import numpy as np


def test_pearson_correlation():
    """Test Pearson correlation calculation"""
    engine = CorrelationEngine()
    
    # Create perfectly correlated series
    x = pd.Series(range(100), index=pd.date_range('2024-01-01', periods=100, freq='min'))
    y = pd.Series(range(100), index=pd.date_range('2024-01-01', periods=100, freq='min'))
    
    coef, p_val = engine.compute_pearson_correlation(x, y)
    
    assert abs(coef - 1.0) < 0.01  # Should be ~1.0
    assert p_val < 0.05  # Should be significant


def test_spearman_correlation():
    """Test Spearman correlation calculation"""
    engine = CorrelationEngine()
    
    # Create monotonic series
    x = pd.Series(np.exp(range(50)), index=pd.date_range('2024-01-01', periods=50, freq='min'))
    y = pd.Series(np.log(range(1, 51)), index=pd.date_range('2024-01-01', periods=50, freq='min'))
    
    coef, p_val = engine.compute_spearman_correlation(x, y)
    
    assert abs(coef) > 0.7  # Should show strong monotonic relationship


def test_lagged_correlation():
    """Test lagged correlation detection"""
    engine = CorrelationEngine()
    
    # Create lagged series
    x = pd.Series(np.sin(np.linspace(0, 4*np.pi, 100)), 
                  index=pd.date_range('2024-01-01', periods=100, freq='min'))
    y_shifted = pd.Series(np.sin(np.linspace(0, 4*np.pi, 100)), 
                          index=pd.date_range('2024-01-01', periods=100, freq='min')).shift(5)
    
    coef, lag = engine.compute_lagged_correlation(x, y_shifted.dropna())
    
    assert abs(coef) > 0.5  # Should detect correlation
    assert abs(lag) > 0  # Should detect lag


def test_granger_causality():
    """Test Granger causality calculation"""
    analyzer = RootCauseAnalyzer()
    
    # Create cause-effect series
    cause = pd.Series(np.random.randn(100).cumsum(), 
                     index=pd.date_range('2024-01-01', periods=100, freq='min'))
    effect = cause.shift(-2) + np.random.randn(100) * 0.1
    
    score, lag = analyzer.granger_causality_test(cause, effect.dropna())
    
    assert score > 0  # Should detect some causal relationship


def test_impact_severity():
    """Test impact severity calculation"""
    assessor = ImpactAssessor()
    
    # Test different severity levels
    assert assessor.calculate_severity(0.9, 1) == "critical"
    assert assessor.calculate_severity(0.7, 2) == "high"
    assert assessor.calculate_severity(0.5, 3) == "medium"
    assert assessor.calculate_severity(0.3, 4) == "low"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
