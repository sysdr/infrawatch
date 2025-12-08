import pytest
import sys
sys.path.insert(0, './backend')
from services.statistics.stats_service import stats_service
from services.anomaly.detector import anomaly_detector
from services.predictor.forecaster import forecaster
import numpy as np

def test_statistics_calculation():
    values = [10, 20, 30, 40, 50]
    stats = stats_service.calculate_stats(values)
    assert stats['mean'] == 30.0
    assert stats['median'] == 30.0
    assert stats['min'] == 10.0
    assert stats['max'] == 50.0

def test_anomaly_detection():
    mean, std = 100, 10
    normal_value = 105
    anomaly_value = 150
    
    result1 = anomaly_detector.detect_statistical_anomaly(normal_value, mean, std)
    assert result1 is None
    
    result2 = anomaly_detector.detect_statistical_anomaly(anomaly_value, mean, std)
    assert result2 is not None
    assert result2['type'] == 'spike'

def test_forecasting():
    values = list(range(1, 51))
    prediction = forecaster.predict_next_value(values, hours_ahead=1)
    assert prediction is not None
    assert 'prediction' in prediction
    assert prediction['prediction'] > 50

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
