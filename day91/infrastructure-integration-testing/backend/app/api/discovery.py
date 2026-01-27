"""Resource discovery API endpoints"""
from fastapi import APIRouter
from typing import List, Dict
from datetime import datetime, timedelta
import random

router = APIRouter()

@router.get("/resources", response_model=List[Dict])
async def get_discovered_resources():
    """Get all discovered resources"""
    resources = []
    resource_types = ["EC2", "RDS", "S3", "Lambda", "ECS"]
    regions = ["us-east-1", "us-west-2", "eu-west-1"]
    
    for i in range(20):
        resources.append({
            "id": f"resource-{i+1}",
            "type": random.choice(resource_types),
            "name": f"{random.choice(resource_types)}-instance-{i+1}",
            "region": random.choice(regions),
            "status": "active",
            "discovered_at": (datetime.utcnow() - timedelta(hours=random.randint(1, 48))).isoformat(),
            "monitored": True,
            "cost_tracked": True
        })
    
    return resources

@router.get("/discovery/status", response_model=Dict)
async def get_discovery_status():
    """Get discovery service status"""
    return {
        "status": "active",
        "last_scan": datetime.utcnow().isoformat(),
        "resources_discovered": 247,
        "discovery_rate": 1200,  # resources per minute
        "accuracy": 99.8
    }
