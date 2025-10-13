from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime
import json

router = APIRouter(prefix="/api/rules", tags=["rules"])

alert_rules = [
    {
        "id": f"rule_{i}",
        "name": f"CPU Threshold Rule {i}",
        "metric": "cpu_usage",
        "condition": "greater_than",
        "threshold": 85 - (i * 5),
        "severity": ["critical", "warning", "info"][i % 3],
        "enabled": True,
        "created_at": (datetime.now()).isoformat(),
        "notifications": ["email", "slack"] if i % 2 else ["email"],
        "tags": ["infrastructure", "cpu"],
        "description": f"Monitor CPU usage for critical infrastructure components"
    }
    for i in range(1, 11)
]

@router.get("/")
async def get_rules():
    """Get all alert rules"""
    return {"rules": alert_rules}

@router.get("/{rule_id}")
async def get_rule(rule_id: str):
    """Get specific rule by ID"""
    rule = next((r for r in alert_rules if r["id"] == rule_id), None)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule

@router.post("/")
async def create_rule(rule_data: dict):
    """Create new alert rule"""
    new_rule = {
        "id": f"rule_{len(alert_rules) + 1}",
        "created_at": datetime.now().isoformat(),
        "enabled": True,
        **rule_data
    }
    alert_rules.append(new_rule)
    return new_rule

@router.put("/{rule_id}")
async def update_rule(rule_id: str, rule_data: dict):
    """Update existing rule"""
    rule = next((r for r in alert_rules if r["id"] == rule_id), None)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    rule.update(rule_data)
    return rule

@router.delete("/{rule_id}")
async def delete_rule(rule_id: str):
    """Delete rule"""
    global alert_rules
    alert_rules = [r for r in alert_rules if r["id"] != rule_id]
    return {"message": "Rule deleted successfully"}

@router.post("/{rule_id}/toggle")
async def toggle_rule(rule_id: str):
    """Toggle rule enabled/disabled"""
    rule = next((r for r in alert_rules if r["id"] == rule_id), None)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    rule["enabled"] = not rule["enabled"]
    return {"message": f"Rule {'enabled' if rule['enabled'] else 'disabled'}"}
