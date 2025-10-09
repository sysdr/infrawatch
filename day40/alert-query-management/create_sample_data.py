#!/usr/bin/env python3
"""
Script to create sample alerts for testing search filters
"""

import requests
import json
from datetime import datetime, timedelta
import random

# Sample alert data
sample_alerts = [
    {
        "title": "Database Connection Timeout",
        "description": "Database connection failed after 30 seconds timeout",
        "severity": "critical",
        "status": "active",
        "source": "monitoring-system",
        "service": "database",
        "environment": "production",
        "tags": ["database", "timeout", "connection"],
        "metadata": {"error_code": "DB_TIMEOUT", "retry_count": 3}
    },
    {
        "title": "High CPU Usage Detected",
        "description": "CPU usage exceeded 90% for more than 5 minutes",
        "severity": "high",
        "status": "active",
        "source": "system-monitor",
        "service": "web-server",
        "environment": "production",
        "tags": ["cpu", "performance", "resource"],
        "metadata": {"cpu_percent": 95, "duration_minutes": 7}
    },
    {
        "title": "Memory Leak Warning",
        "description": "Memory usage increasing steadily over time",
        "severity": "medium",
        "status": "acknowledged",
        "source": "monitoring-system",
        "service": "api-gateway",
        "environment": "staging",
        "tags": ["memory", "leak", "performance"],
        "metadata": {"memory_mb": 2048, "trend": "increasing"}
    },
    {
        "title": "SSL Certificate Expiring Soon",
        "description": "SSL certificate expires in 30 days",
        "severity": "low",
        "status": "resolved",
        "source": "certificate-monitor",
        "service": "web-server",
        "environment": "production",
        "tags": ["ssl", "certificate", "security"],
        "metadata": {"expiry_date": "2025-02-15", "days_remaining": 30}
    },
    {
        "title": "Disk Space Low",
        "description": "Disk usage exceeded 85% on /var partition",
        "severity": "high",
        "status": "suppressed",
        "source": "system-monitor",
        "service": "file-server",
        "environment": "production",
        "tags": ["disk", "storage", "space"],
        "metadata": {"partition": "/var", "usage_percent": 87}
    },
    {
        "title": "API Response Time Slow",
        "description": "API response time exceeded 2 seconds",
        "severity": "medium",
        "status": "active",
        "source": "api-monitor",
        "service": "api-gateway",
        "environment": "production",
        "tags": ["api", "performance", "latency"],
        "metadata": {"response_time_ms": 2500, "endpoint": "/api/users"}
    },
    {
        "title": "Failed Login Attempts",
        "description": "Multiple failed login attempts detected",
        "severity": "critical",
        "status": "active",
        "source": "security-monitor",
        "service": "auth-service",
        "environment": "production",
        "tags": ["security", "login", "authentication"],
        "metadata": {"attempts": 15, "ip_address": "192.168.1.100"}
    },
    {
        "title": "Backup Job Failed",
        "description": "Scheduled backup job failed to complete",
        "severity": "medium",
        "status": "resolved",
        "source": "backup-system",
        "service": "backup-service",
        "environment": "production",
        "tags": ["backup", "job", "failure"],
        "metadata": {"job_id": "backup_20250109", "error": "disk_full"}
    }
]

def create_sample_alerts():
    """Create sample alerts in the database"""
    base_url = "http://localhost:8000"
    
    print("Creating sample alerts...")
    
    for i, alert_data in enumerate(sample_alerts):
        # Add some time variation to the alerts
        base_time = datetime.now() - timedelta(hours=random.randint(1, 72))
        alert_data["created_at"] = base_time.isoformat()
        
        # For resolved alerts, set resolved_at
        if alert_data["status"] == "resolved":
            alert_data["resolved_at"] = (base_time + timedelta(hours=random.randint(1, 24))).isoformat()
        
        # For acknowledged alerts, set acknowledged_at
        if alert_data["status"] == "acknowledged":
            alert_data["acknowledged_at"] = (base_time + timedelta(minutes=random.randint(5, 60))).isoformat()
            alert_data["acknowledged_by"] = "admin@example.com"
        
        print(f"Creating alert {i+1}: {alert_data['title']}")
        
        # Note: Since we don't have a direct create endpoint, we'll use the search endpoint
        # to verify the alerts exist. In a real scenario, you'd have a POST /api/alerts endpoint.
        # For now, let's just print what we would create.
        print(f"  - Severity: {alert_data['severity']}")
        print(f"  - Status: {alert_data['status']}")
        print(f"  - Source: {alert_data['source']}")
        print(f"  - Service: {alert_data['service']}")
        print(f"  - Tags: {alert_data['tags']}")
        print()

if __name__ == "__main__":
    create_sample_alerts()
    print("Sample alert data prepared!")
    print("\nNote: In a real system, you would have a POST /api/alerts endpoint to create alerts.")
    print("For demonstration purposes, we'll show you how to search with these filter examples.")