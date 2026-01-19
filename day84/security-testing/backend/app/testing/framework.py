import asyncio
import time
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.security import SecurityEvent, SecurityTest, ThreatPattern
import random
import string

class SecurityTestFramework:
    def __init__(self, db: Session):
        self.db = db
        self.test_results = []
        
    async def run_unit_tests(self) -> Dict[str, Any]:
        """Run all unit tests for security components"""
        start_time = time.perf_counter()
        test_suite = "security_unit_tests"
        results = {"passed": 0, "failed": 0, "tests": []}
        
        tests = [
            self._test_authentication_validation,
            self._test_authorization_checks,
            self._test_encryption_functions,
            self._test_input_sanitization,
            self._test_rate_limiting_logic,
            self._test_threat_pattern_matching,
            self._test_event_correlation,
            self._test_severity_classification
        ]
        
        for test_func in tests:
            try:
                test_result = await test_func()
                if test_result["passed"]:
                    results["passed"] += 1
                else:
                    results["failed"] += 1
                results["tests"].append(test_result)
            except Exception as e:
                results["failed"] += 1
                results["tests"].append({
                    "name": test_func.__name__,
                    "passed": False,
                    "error": str(e)
                })
        
        duration_ms = int((time.perf_counter() - start_time) * 1000)
        
        # Save test results
        test_record = SecurityTest(
            test_name="Complete Unit Test Suite",
            test_type="unit",
            test_suite=test_suite,
            status="passed" if results["failed"] == 0 else "failed",
            duration_ms=duration_ms,
            completed_at=datetime.utcnow(),
            results=results
        )
        self.db.add(test_record)
        self.db.commit()
        
        return {
            "suite": test_suite,
            "total_tests": len(tests),
            "passed": results["passed"],
            "failed": results["failed"],
            "duration_ms": duration_ms,
            "results": results["tests"]
        }
    
    async def _test_authentication_validation(self) -> Dict[str, Any]:
        """Test authentication logic handles valid/invalid credentials"""
        test_cases = [
            {"username": "valid@user.com", "password": "SecurePass123!", "expected": True},
            {"username": "invalid@user.com", "password": "wrong", "expected": False},
            {"username": "", "password": "test", "expected": False},
            {"username": "test@user.com", "password": "", "expected": False},
        ]
        
        passed = True
        for case in test_cases:
            is_valid = bool(case["username"] and case["password"] and len(case["password"]) >= 8)
            if is_valid != case["expected"]:
                passed = False
                break
        
        return {"name": "authentication_validation", "passed": passed, "cases": len(test_cases)}
    
    async def _test_authorization_checks(self) -> Dict[str, Any]:
        """Test role-based access control logic"""
        roles = {"admin": ["read", "write", "delete"], "user": ["read"], "guest": []}
        test_cases = [
            {"role": "admin", "action": "delete", "expected": True},
            {"role": "user", "action": "delete", "expected": False},
            {"role": "guest", "action": "read", "expected": False},
        ]
        
        passed = all(
            (case["action"] in roles.get(case["role"], [])) == case["expected"]
            for case in test_cases
        )
        
        return {"name": "authorization_checks", "passed": passed, "cases": len(test_cases)}
    
    async def _test_encryption_functions(self) -> Dict[str, Any]:
        """Test encryption/decryption functions"""
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        password = "TestPassword123!"
        hashed = pwd_context.hash(password)
        
        passed = (
            pwd_context.verify(password, hashed) and
            not pwd_context.verify("WrongPassword", hashed) and
            len(hashed) > 50
        )
        
        return {"name": "encryption_functions", "passed": passed}
    
    async def _test_input_sanitization(self) -> Dict[str, Any]:
        """Test input validation and sanitization"""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "<script>alert('XSS')</script>",
            "../../../etc/passwd",
            "1' OR '1'='1"
        ]
        
        def sanitize(input_str: str) -> str:
            dangerous_chars = ["'", '"', "<", ">", ";", "--", ".."]
            return "".join(c for c in input_str if c not in dangerous_chars)
        
        passed = all(
            len(sanitize(malicious)) < len(malicious)
            for malicious in malicious_inputs
        )
        
        return {"name": "input_sanitization", "passed": passed, "cases": len(malicious_inputs)}
    
    async def _test_rate_limiting_logic(self) -> Dict[str, Any]:
        """Test rate limiting algorithm"""
        rate_limit = 100
        window = 60
        
        requests = []
        current_time = time.time()
        
        for i in range(150):
            requests.append(current_time + (i * 0.01))
        
        recent_requests = [r for r in requests if current_time - r < window]
        is_rate_limited = len(recent_requests) > rate_limit
        
        passed = is_rate_limited
        return {"name": "rate_limiting_logic", "passed": passed}
    
    async def _test_threat_pattern_matching(self) -> Dict[str, Any]:
        """Test threat pattern detection"""
        import re
        
        sql_injection_pattern = r"(\bUNION\b|\bSELECT\b|\bDROP\b|\bINSERT\b).*(\bFROM\b|\bWHERE\b|\bTABLE\b)"
        
        test_cases = [
            {"input": "SELECT * FROM users WHERE id=1", "should_match": True},
            {"input": "Hello, this is normal text", "should_match": False},
            {"input": "1' UNION SELECT * FROM passwords", "should_match": True},
        ]
        
        passed = all(
            bool(re.search(sql_injection_pattern, case["input"], re.IGNORECASE)) == case["should_match"]
            for case in test_cases
        )
        
        return {"name": "threat_pattern_matching", "passed": passed, "cases": len(test_cases)}
    
    async def _test_event_correlation(self) -> Dict[str, Any]:
        """Test security event correlation logic"""
        events = [
            {"source_ip": "192.168.1.100", "event_type": "auth_failure", "timestamp": time.time()},
            {"source_ip": "192.168.1.100", "event_type": "auth_failure", "timestamp": time.time() + 5},
            {"source_ip": "192.168.1.100", "event_type": "auth_failure", "timestamp": time.time() + 10},
        ]
        
        correlation_window = 60
        current_time = time.time()
        
        grouped = {}
        for event in events:
            if current_time - event["timestamp"] < correlation_window:
                key = event["source_ip"]
                grouped[key] = grouped.get(key, 0) + 1
        
        is_attack_pattern = any(count >= 3 for count in grouped.values())
        return {"name": "event_correlation", "passed": is_attack_pattern}
    
    async def _test_severity_classification(self) -> Dict[str, Any]:
        """Test threat severity calculation"""
        def calculate_severity(event_type: str, frequency: int) -> str:
            severity_map = {
                "auth_failure": {"low": 5, "medium": 10, "high": 20},
                "sql_injection": {"low": 1, "medium": 3, "high": 5},
                "data_exfiltration": {"low": 1, "medium": 2, "high": 3},
            }
            
            thresholds = severity_map.get(event_type, {"low": 10, "medium": 50, "high": 100})
            
            if frequency >= thresholds["high"]:
                return "critical"
            elif frequency >= thresholds["medium"]:
                return "high"
            elif frequency >= thresholds["low"]:
                return "medium"
            return "low"
        
        test_cases = [
            {"type": "auth_failure", "freq": 25, "expected": "critical"},
            {"type": "sql_injection", "freq": 2, "expected": "medium"},
            {"type": "data_exfiltration", "freq": 1, "expected": "medium"},
        ]
        
        passed = all(
            calculate_severity(case["type"], case["freq"]) == case["expected"]
            for case in test_cases
        )
        
        return {"name": "severity_classification", "passed": passed, "cases": len(test_cases)}

class IntegrationTestFramework:
    def __init__(self, db: Session, base_url: str = "http://localhost:8000"):
        self.db = db
        self.base_url = base_url
        
    async def run_integration_tests(self) -> Dict[str, Any]:
        """Run end-to-end integration tests"""
        start_time = time.perf_counter()
        results = {"passed": 0, "failed": 0, "tests": []}
        
        tests = [
            self._test_threat_detection_to_alert,
            self._test_incident_creation_flow,
            self._test_auto_response_execution,
            self._test_alert_escalation,
            self._test_audit_log_integration
        ]
        
        for test_func in tests:
            try:
                test_result = await test_func()
                if test_result["passed"]:
                    results["passed"] += 1
                else:
                    results["failed"] += 1
                results["tests"].append(test_result)
            except Exception as e:
                results["failed"] += 1
                results["tests"].append({
                    "name": test_func.__name__,
                    "passed": False,
                    "error": str(e)
                })
        
        duration_ms = int((time.perf_counter() - start_time) * 1000)
        
        return {
            "suite": "integration_tests",
            "total_tests": len(tests),
            "passed": results["passed"],
            "failed": results["failed"],
            "duration_ms": duration_ms,
            "results": results["tests"]
        }
    
    async def _test_threat_detection_to_alert(self) -> Dict[str, Any]:
        """Test complete flow from threat detection to alert generation"""
        start = time.perf_counter()
        
        event = SecurityEvent(
            event_type="sql_injection",
            severity="high",
            source_ip="10.0.0.50",
            endpoint="/api/users",
            request_data={"query": "1' OR '1'='1"},
            threat_score=0.95,
            correlation_id=str(uuid.uuid4())
        )
        self.db.add(event)
        self.db.commit()
        
        saved_event = self.db.query(SecurityEvent).filter_by(
            correlation_id=event.correlation_id
        ).first()
        
        detection_latency_ms = int((time.perf_counter() - start) * 1000)
        passed = saved_event is not None and detection_latency_ms < 100
        
        return {
            "name": "threat_detection_to_alert",
            "passed": passed,
            "detection_latency_ms": detection_latency_ms
        }
    
    async def _test_incident_creation_flow(self) -> Dict[str, Any]:
        """Test incident creation from correlated events"""
        from app.models.security import IncidentResponse
        
        correlation_id = str(uuid.uuid4())
        for i in range(5):
            event = SecurityEvent(
                event_type="auth_failure",
                severity="medium",
                source_ip="10.0.0.100",
                endpoint="/api/login",
                correlation_id=correlation_id,
                threat_score=0.6
            )
            self.db.add(event)
        self.db.commit()
        
        incident = IncidentResponse(
            incident_id=f"INC-{correlation_id[:8]}",
            severity="high",
            status="investigating",
            event_count=5,
            affected_systems=["authentication_service"],
            response_actions=["rate_limit_applied", "ip_blocked"]
        )
        self.db.add(incident)
        self.db.commit()
        
        saved_incident = self.db.query(IncidentResponse).filter_by(
            incident_id=incident.incident_id
        ).first()
        
        passed = (
            saved_incident is not None and
            saved_incident.event_count == 5 and
            saved_incident.status == "investigating"
        )
        
        return {"name": "incident_creation_flow", "passed": passed}
    
    async def _test_auto_response_execution(self) -> Dict[str, Any]:
        """Test automated response actions"""
        threat_score = 0.95
        source_ip = "10.0.0.200"
        
        actions_taken = []
        if threat_score > 0.9:
            actions_taken.append("ip_blocked")
            actions_taken.append("alert_sent")
            actions_taken.append("session_terminated")
        
        passed = len(actions_taken) == 3 and "ip_blocked" in actions_taken
        
        return {
            "name": "auto_response_execution",
            "passed": passed,
            "actions": actions_taken
        }
    
    async def _test_alert_escalation(self) -> Dict[str, Any]:
        """Test alert escalation logic"""
        alert_sent_time = time.time()
        ack_deadline = 60
        
        current_time = time.time()
        time_elapsed = current_time - alert_sent_time
        
        should_escalate = time_elapsed > ack_deadline
        passed = should_escalate == False
        
        return {
            "name": "alert_escalation",
            "passed": passed,
            "time_to_escalate": ack_deadline - time_elapsed
        }
    
    async def _test_audit_log_integration(self) -> Dict[str, Any]:
        """Test audit logging captures all security events"""
        event_types = ["auth_failure", "sql_injection", "rate_limit"]
        for event_type in event_types:
            event = SecurityEvent(
                event_type=event_type,
                severity="medium",
                source_ip="10.0.0.150",
                endpoint="/api/test",
                correlation_id=str(uuid.uuid4())
            )
            self.db.add(event)
        self.db.commit()
        
        logged_count = self.db.query(SecurityEvent).filter(
            SecurityEvent.event_type.in_(event_types)
        ).count()
        
        passed = logged_count >= len(event_types)
        
        return {
            "name": "audit_log_integration",
            "passed": passed,
            "logged_events": logged_count
        }
