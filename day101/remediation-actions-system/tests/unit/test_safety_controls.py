import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from app.services.safety_controls import SafetyControls

def test_blast_radius_calculation():
    controls = SafetyControls("redis://localhost:6379")
    params = {"ip_address": "192.168.1.1"}
    radius = controls.calculate_blast_radius(params, 100)
    assert radius == 1
    params = {"ip_addresses": ["192.168.1.1", "192.168.1.2", "192.168.1.3"]}
    radius = controls.calculate_blast_radius(params, 100)
    assert radius == 3

def test_risk_score_calculation():
    controls = SafetyControls("redis://localhost:6379")
    score = controls.calculate_risk_score("low", 1, {})
    assert score < 50
    score = controls.calculate_risk_score("high", 50, {})
    assert score > 75

def test_validate_blast_radius():
    controls = SafetyControls("redis://localhost:6379")
    valid, error = controls.validate_blast_radius(5, 10, 100)
    assert valid is True
    assert error is None
    valid, error = controls.validate_blast_radius(15, 10, 100)
    assert valid is False
    assert "template" in error
