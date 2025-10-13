from datetime import datetime, timedelta

# Sample alert data (in production, this would be from database)
sample_alerts = [
    {
        "id": f"alert_{i}",
        "title": f"High CPU Usage - Server {i%3 + 1}",
        "severity": ["critical", "warning", "info"][i % 3],
        "status": ["active", "acknowledged", "resolved"][i % 3],
        "timestamp": (datetime.now() - timedelta(minutes=i*10)).isoformat(),
        "description": f"CPU usage above 85% for server-{i%3 + 1}",
        "source": f"server-{i%3 + 1}",
        "tags": ["infrastructure", "cpu", "performance"],
        "assignee": f"engineer_{i%4 + 1}" if i % 2 else None,
        "rule_id": f"rule_{i%5 + 1}",
        "metric_value": 85 + (i % 15),
        "threshold": 85,
        "history": [
            {
                "action": "created",
                "timestamp": (datetime.now() - timedelta(minutes=i*10)).isoformat(),
                "user": "system",
                "note": "Alert triggered by monitoring system"
            },
            {
                "action": "acknowledged" if i % 2 else "assigned",
                "timestamp": (datetime.now() - timedelta(minutes=i*10-5)).isoformat(),
                "user": f"engineer_{i%4 + 1}",
                "note": "Investigating the issue"
            }
        ] if i % 3 != 2 else []
    }
    for i in range(100)
]

alert_rules = [
    {
        "id": f"rule_{i}",
        "name": f"CPU Threshold Rule {i}",
        "metric": "cpu_usage",
        "condition": "greater_than",
        "threshold": 85,
        "severity": ["critical", "warning"][i % 2],
        "enabled": True,
        "created_at": (datetime.now() - timedelta(days=i)).isoformat(),
        "notifications": ["email", "slack"],
        "tags": ["infrastructure", "cpu"]
    }
    for i in range(1, 6)
]
