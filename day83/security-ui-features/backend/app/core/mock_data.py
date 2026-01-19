"""Mock data generator for when database is unavailable"""
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random

def get_mock_dashboard_metrics() -> Dict[str, Any]:
    """Generate mock dashboard metrics"""
    now = datetime.utcnow()
    return {
        "active_threats": random.randint(5, 25),
        "events_last_hour": random.randint(10, 100),
        "avg_threat_score": round(random.uniform(50, 85), 2),
        "event_trend": [
            {
                "date": (now - timedelta(days=6-i)).strftime("%Y-%m-%d"),
                "count": random.randint(50, 200)
            }
            for i in range(7)
        ],
        "timestamp": now.isoformat()
    }

def get_mock_threat_distribution() -> Dict[str, Any]:
    """Generate mock threat distribution"""
    severities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    event_types = [
        "Unauthorized Access Attempt",
        "Malware Detection",
        "Data Exfiltration",
        "Privilege Escalation",
        "Network Intrusion",
        "Suspicious Activity",
        "Policy Violation",
        "Account Compromise"
    ]
    
    return {
        "severity_distribution": [
            {"severity": sev, "count": random.randint(10, 100)}
            for sev in severities
        ],
        "type_distribution": [
            {"event_type": etype, "count": random.randint(5, 50)}
            for etype in event_types[:8]
        ]
    }

def get_mock_timeline(hours: int = 24) -> Dict[str, Any]:
    """Generate mock timeline data"""
    start_time = datetime.utcnow() - timedelta(hours=hours)
    timeline_data = []
    
    for i in range(hours):
        hour_start = start_time + timedelta(hours=i)
        timeline_data.append({
            "timestamp": hour_start.isoformat(),
            "total_events": random.randint(0, 50),
            "critical": random.randint(0, 5),
            "high": random.randint(0, 10),
            "medium": random.randint(0, 20),
            "low": random.randint(0, 30)
        })
    
    return {"timeline": timeline_data}

def get_mock_security_events(limit: int = 20) -> List[Dict[str, Any]]:
    """Generate mock security events"""
    event_types = [
        "Unauthorized Access Attempt",
        "Malware Detection",
        "Data Exfiltration",
        "Privilege Escalation",
        "Network Intrusion"
    ]
    severities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    sources = ["192.168.1.100", "10.0.0.50", "172.16.0.25", "external"]
    destinations = ["192.168.1.1", "10.0.0.1", "172.16.0.1", None]
    user_agents = ["Mozilla/5.0", "curl/7.68.0", "Python-requests/2.28.0", None]
    users = ["user1", "user2", "admin", None]
    
    events = []
    for i in range(limit):
        created_at = datetime.utcnow() - timedelta(hours=random.randint(0, 48))
        is_resolved = random.choice([True, False])
        resolved_by = random.choice(["admin", "system", None]) if is_resolved else None
        resolved_at = (created_at + timedelta(hours=random.randint(1, 24))).isoformat() if is_resolved else None
        
        events.append({
            "id": i + 1,
            "event_id": f"mock-event-{i+1}",
            "event_type": random.choice(event_types),
            "severity": random.choice(severities),
            "source": random.choice(sources),
            "destination": random.choice(destinations),
            "user_id": random.choice(users),
            "ip_address": random.choice(sources),
            "user_agent": random.choice(user_agents),
            "description": f"Mock security event {i+1}",
            "event_metadata": {"mock": True, "test_data": True},
            "threat_score": random.randint(30, 95),
            "is_resolved": is_resolved,
            "resolved_by": resolved_by,
            "resolved_at": resolved_at,
            "created_at": created_at.isoformat()
        })
    
    return events

def get_mock_event_summary() -> Dict[str, Any]:
    """Generate mock event summary"""
    return {
        "total_events": random.randint(500, 2000),
        "unresolved_events": random.randint(50, 200),
        "severity_breakdown": {
            "LOW": random.randint(200, 800),
            "MEDIUM": random.randint(150, 600),
            "HIGH": random.randint(50, 200),
            "CRITICAL": random.randint(10, 50)
        },
        "events_last_24h": random.randint(50, 300)
    }

def get_mock_audit_logs(limit: int = 20) -> List[Dict[str, Any]]:
    """Generate mock audit logs"""
    actions = ["LOGIN", "LOGOUT", "SETTING_CHANGE", "EVENT_RESOLVE", "REPORT_GENERATE"]
    results = ["success", "failure"]
    users = ["admin", "operator", "analyst", "system"]
    resource_types = ["security_event", "security_setting", "report", "user", "session"]
    user_agents = ["Mozilla/5.0", "curl/7.68.0", "Python-requests/2.28.0", None]
    
    logs = []
    for i in range(limit):
        created_at = datetime.utcnow() - timedelta(hours=random.randint(0, 72))
        action = random.choice(actions)
        # Map actions to appropriate resource types
        if action == "SETTING_CHANGE":
            resource_type = "security_setting"
        elif action == "EVENT_RESOLVE":
            resource_type = "security_event"
        elif action == "REPORT_GENERATE":
            resource_type = "report"
        elif action in ["LOGIN", "LOGOUT"]:
            resource_type = "session"
        else:
            resource_type = "user"
        
        logs.append({
            "id": i + 1,
            "log_id": f"audit-{i+1}",
            "action_type": action,
            "actor": random.choice(users),
            "resource_type": resource_type,
            "resource_id": f"res-{random.randint(1, 100)}",
            "action_result": random.choice(results),
            "ip_address": f"192.168.1.{random.randint(1, 255)}",
            "user_agent": random.choice(user_agents),
            "before_state": {"status": "active"} if action == "SETTING_CHANGE" else None,
            "after_state": {"status": "modified"} if action == "SETTING_CHANGE" else None,
            "audit_metadata": {"mock": True, "test_data": True},
            "created_at": created_at.isoformat()
        })
    
    return logs

def get_mock_settings() -> List[Dict[str, Any]]:
    """Generate mock settings"""
    now = datetime.utcnow()
    return [
        {
            "id": 1,
            "setting_key": "alert_threshold",
            "setting_name": "Alert Threshold",
            "setting_value": {"value": 75, "unit": "score"},
            "category": "alerts",
            "description": "Alert threshold for threat score",
            "is_active": True,
            "modified_by": "admin",
            "created_at": (now - timedelta(days=30)).isoformat(),
            "updated_at": (now - timedelta(days=5)).isoformat()
        },
        {
            "id": 2,
            "setting_key": "auto_resolve_low",
            "setting_name": "Auto Resolve Low Severity",
            "setting_value": {"enabled": False},
            "category": "automation",
            "description": "Automatically resolve low severity events",
            "is_active": True,
            "modified_by": "admin",
            "created_at": (now - timedelta(days=30)).isoformat(),
            "updated_at": (now - timedelta(days=10)).isoformat()
        },
        {
            "id": 3,
            "setting_key": "retention_days",
            "setting_name": "Data Retention Period",
            "setting_value": {"days": 90},
            "category": "data",
            "description": "Number of days to retain events",
            "is_active": True,
            "modified_by": "admin",
            "created_at": (now - timedelta(days=30)).isoformat(),
            "updated_at": (now - timedelta(days=2)).isoformat()
        },
        {
            "id": 4,
            "setting_key": "notification_email",
            "setting_name": "Notification Email",
            "setting_value": {"email": "security@example.com"},
            "category": "notifications",
            "description": "Email address for security alerts",
            "is_active": True,
            "modified_by": "admin",
            "created_at": (now - timedelta(days=20)).isoformat(),
            "updated_at": (now - timedelta(days=1)).isoformat()
        },
        {
            "id": 5,
            "setting_key": "log_level",
            "setting_name": "Logging Level",
            "setting_value": {"level": "INFO"},
            "category": "logging",
            "description": "Application logging level",
            "is_active": True,
            "modified_by": "system",
            "created_at": (now - timedelta(days=30)).isoformat(),
            "updated_at": (now - timedelta(days=15)).isoformat()
        }
    ]

def get_mock_reports() -> Dict[str, Any]:
    """Generate mock reports"""
    now = datetime.utcnow()
    today = now.date()
    
    # Daily report
    total_events = random.randint(100, 500)
    resolved_events = random.randint(50, 200)
    daily_report = {
        "report_date": today.isoformat(),
        "total_events": total_events,
        "critical_events": random.randint(5, 25),
        "resolved_events": resolved_events,
        "resolution_rate": round((resolved_events / total_events * 100) if total_events > 0 else 0, 2),
        "top_event_types": [
            {"event_type": "Unauthorized Access Attempt", "count": random.randint(20, 80)},
            {"event_type": "Malware Detection", "count": random.randint(15, 60)},
            {"event_type": "Network Intrusion", "count": random.randint(10, 50)},
            {"event_type": "Privilege Escalation", "count": random.randint(5, 30)},
            {"event_type": "Data Exfiltration", "count": random.randint(3, 20)}
        ]
    }
    
    # Weekly report - generate daily breakdown
    start_date = now - timedelta(days=7)
    daily_breakdown = []
    for i in range(7):
        day = start_date + timedelta(days=i)
        daily_breakdown.append({
            "date": day.strftime("%Y-%m-%d"),
            "total_events": random.randint(50, 200),
            "critical": random.randint(0, 10),
            "high": random.randint(5, 25),
            "medium": random.randint(10, 50),
            "low": random.randint(20, 100)
        })
    
    weekly_report = {
        "report_period": {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": now.strftime("%Y-%m-%d")
        },
        "daily_breakdown": daily_breakdown
    }
    
    # Compliance report
    total_security_events = random.randint(1000, 5000)
    critical_unresolved = random.randint(5, 20)
    compliance_report = {
        "report_period": "Last 30 days",
        "security_events": {
            "total": total_security_events,
            "critical_unresolved": critical_unresolved,
            "compliance_status": "PASS" if critical_unresolved == 0 else "REVIEW_REQUIRED"
        },
        "audit_coverage": {
            "total_logs": random.randint(1000, 5000),
            "coverage": "ADEQUATE" if random.randint(0, 1) else "NEEDS_IMPROVEMENT"
        },
        "generated_at": now.isoformat()
    }
    
    return {
        "daily": daily_report,
        "weekly": weekly_report,
        "compliance": compliance_report
    }
