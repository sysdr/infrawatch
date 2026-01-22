from fastapi import APIRouter
from typing import List, Dict
from datetime import datetime, timedelta
import random

router = APIRouter()

@router.get("/events", response_model=List[Dict])
async def get_autoscaling_events(hours: int = 24):
    """Get recent auto-scaling events"""
    # Simulate auto-scaling events
    events = []
    
    for i in range(5):
        event_time = datetime.utcnow() - timedelta(hours=random.randint(0, hours))
        
        events.append({
            'id': i + 1,
            'group_name': f'web-servers-asg-{random.randint(1, 3)}',
            'region': random.choice(['us-east-1', 'us-west-2']),
            'event_type': random.choice(['scale_up', 'scale_down']),
            'trigger_metric': 'CPUUtilization',
            'trigger_value': random.uniform(60, 95),
            'old_capacity': random.randint(2, 10),
            'new_capacity': random.randint(2, 10),
            'cost_impact': random.uniform(5, 50),
            'timestamp': event_time.isoformat()
        })
    
    return sorted(events, key=lambda x: x['timestamp'], reverse=True)

@router.get("/groups")
async def get_autoscaling_groups():
    """Get auto-scaling group status"""
    return [
        {
            'name': 'web-servers-asg-1',
            'region': 'us-east-1',
            'desired_capacity': 4,
            'current_capacity': 4,
            'min_capacity': 2,
            'max_capacity': 10,
            'health_check_type': 'ELB',
            'scaling_policies': 2
        },
        {
            'name': 'api-servers-asg-1',
            'region': 'us-west-2',
            'desired_capacity': 6,
            'current_capacity': 6,
            'min_capacity': 3,
            'max_capacity': 15,
            'health_check_type': 'EC2',
            'scaling_policies': 3
        }
    ]
