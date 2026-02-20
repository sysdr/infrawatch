import pytest
import numpy as np

def test_pearson_correlation():
    """Test that perfectly correlated series returns 1.0"""
    from scipy.stats import pearsonr
    x = np.arange(100, dtype=float)
    y = x * 2 + 5
    coef, _ = pearsonr(x, y)
    assert abs(coef - 1.0) < 1e-6

def test_spearman_correlation():
    from scipy.stats import spearmanr
    x = np.arange(50, dtype=float)
    y = -x  # perfectly negative
    coef, _ = spearmanr(x, y)
    assert abs(coef - (-1.0)) < 1e-6

def test_feature_importance_keys():
    """Feature importance dict must have all expected features."""
    from app.services.ml_service import FEATURE_NAMES
    assert len(FEATURE_NAMES) == 6
    assert "cpu_utilization" in FEATURE_NAMES
    assert "error_rate" in FEATURE_NAMES

def test_kpi_trend_direction():
    """Trend direction logic."""
    current, previous = 80.0, 70.0
    trend = ((current - previous) / max(previous, 0.001)) * 100
    direction = "up" if trend > 0 else "down"
    assert direction == "up"
    assert round(trend, 1) == 14.3
