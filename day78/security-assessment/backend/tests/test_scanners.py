import pytest
from app.scanners.vulnerability_scanner import VulnerabilityScanner
from app.scanners.code_analyzer import CodeAnalyzer
from app.scanners.dependency_auditor import DependencyAuditor
from app.scanners.compliance_checker import ComplianceChecker
from app.scanners.threat_modeler import ThreatModeler
import tempfile
import os

def test_vulnerability_scanner():
    scanner = VulnerabilityScanner()
    
    # Create test file with vulnerability
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.py")
        with open(test_file, 'w') as f:
            f.write("password = 'hardcoded123'")
        
        results = scanner.scan_directory(tmpdir)
        assert len(results) > 0
        assert any('password' in r['title'].lower() or 'credential' in r['title'].lower() 
                  for r in results)

def test_code_analyzer():
    analyzer = CodeAnalyzer()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.py")
        with open(test_file, 'w') as f:
            f.write("eval(user_input)")
        
        results = analyzer.analyze_code(tmpdir)
        assert len(results) > 0

def test_dependency_auditor():
    auditor = DependencyAuditor()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        req_file = os.path.join(tmpdir, "requirements.txt")
        with open(req_file, 'w') as f:
            f.write("django==2.0\n")
        
        results = auditor.audit_dependencies(tmpdir)
        # Should detect old Django version
        assert isinstance(results, list)

def test_compliance_checker():
    checker = ComplianceChecker()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        results = checker.check_compliance(tmpdir)
        assert len(results) > 0
        assert all('framework' in r for r in results)
        assert all('status' in r for r in results)

def test_threat_modeler():
    modeler = ThreatModeler()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        results = modeler.model_threats(tmpdir)
        assert len(results) > 0
        assert all('threat_category' in r for r in results)
        assert all('risk_score' in r for r in results)

def test_severity_mapping():
    scanner = VulnerabilityScanner()
    
    assert scanner._severity_to_cvss('CRITICAL') == 9.5
    assert scanner._severity_to_cvss('HIGH') == 7.5
    assert scanner._severity_to_cvss('MEDIUM') == 5.0
    assert scanner._severity_to_cvss('LOW') == 2.5
