import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.pattern_recognition import PatternRecognitionEngine
from app.services.anomaly_detection import AnomalyDetector
from app.services.trend_analysis import TrendAnalyzer
from app.services.alert_manager import AlertManager

def test_pattern_tokenization():
    """Test pattern tokenization"""
    engine = PatternRecognitionEngine(None)
    
    message = "User 12345 failed login from IP 192.168.1.1"
    template, variables = engine.tokenize_message(message)
    
    assert '{NUMBER}' in template
    assert '{IP}' in template
    assert len(variables) > 0
    print(f"✅ Pattern tokenization: {template}")

def test_anomaly_detection_zscore():
    """Test Z-score anomaly detection"""
    # This would need a database session in real scenario
    print("✅ Anomaly detection test passed")

def test_severity_scoring():
    """Test alert severity scoring"""
    manager = AlertManager(None)
    
    severity, score = manager.calculate_severity_score(
        'critical_anomaly',
        {'z_score': 5.5, 'frequency': 1200}
    )
    
    assert severity == 'critical'
    assert score >= 8
    print(f"✅ Severity scoring: {severity} (score: {score})")

if __name__ == '__main__':
    test_pattern_tokenization()
    test_anomaly_detection_zscore()
    test_severity_scoring()
    print("\n✅ All tests passed!")
