from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import random

router = APIRouter()

class TrackingEvent(BaseModel):
    event_type: str
    timestamp: datetime
    description: str
    metadata: Optional[Dict[str, Any]] = None

class NotificationTracking(BaseModel):
    tracking_id: str
    notification_id: str
    current_status: str
    created_at: datetime
    events: List[TrackingEvent]

# Mock tracking data
tracking_data: Dict[str, NotificationTracking] = {}

@router.get("/{tracking_id}", response_model=NotificationTracking)
async def track_notification(tracking_id: str):
    """Track notification by tracking ID"""
    
    # Generate demo tracking data if not exists
    if tracking_id not in tracking_data:
        # Create realistic tracking events
        base_time = datetime.now() - timedelta(minutes=random.randint(5, 60))
        
        events = [
            TrackingEvent(
                event_type="queued",
                timestamp=base_time,
                description="Notification added to delivery queue",
                metadata={"priority": "normal", "queue_position": random.randint(1, 100)}
            ),
            TrackingEvent(
                event_type="processing",
                timestamp=base_time + timedelta(seconds=random.randint(10, 120)),
                description="Notification picked up for processing",
                metadata={"worker_id": "worker_1", "attempt": 1}
            )
        ]
        
        # Add delivery event
        delivery_time = base_time + timedelta(seconds=random.randint(130, 300))
        if random.random() < 0.85:  # 85% success rate
            events.append(TrackingEvent(
                event_type="delivered",
                timestamp=delivery_time,
                description="Notification delivered successfully",
                metadata={"delivery_time_ms": random.randint(150, 350)}
            ))
            current_status = "delivered"
            
            # Maybe add read event
            if random.random() < 0.3:  # 30% read rate
                events.append(TrackingEvent(
                    event_type="read",
                    timestamp=delivery_time + timedelta(minutes=random.randint(1, 30)),
                    description="Notification read by recipient",
                    metadata={"read_time_ms": random.randint(2000, 10000)}
                ))
                current_status = "read"
        else:
            events.append(TrackingEvent(
                event_type="failed",
                timestamp=delivery_time,
                description="Delivery failed - recipient unreachable",
                metadata={"error_code": "RECIPIENT_UNREACHABLE", "retry_scheduled": True}
            ))
            current_status = "failed"
        
        tracking_data[tracking_id] = NotificationTracking(
            tracking_id=tracking_id,
            notification_id=f"notif_{tracking_id.split('_')[1]}",
            current_status=current_status,
            created_at=base_time,
            events=events
        )
    
    return tracking_data[tracking_id]

@router.get("/")
async def list_tracking():
    """List recent tracking entries"""
    # Generate some demo data
    demo_tracking = []
    for i in range(20):
        tracking_id = f"track_{i:04d}"
        base_time = datetime.now() - timedelta(minutes=random.randint(1, 120))
        
        demo_tracking.append({
            "tracking_id": tracking_id,
            "notification_id": f"notif_{i:04d}",
            "status": random.choice(["delivered", "failed", "processing", "queued"]),
            "channel": random.choice(["email", "sms", "push"]),
            "created_at": base_time.isoformat(),
            "last_updated": (base_time + timedelta(seconds=random.randint(30, 300))).isoformat()
        })
    
    return {"tracking_entries": demo_tracking}

@router.post("/{tracking_id}/events")
async def add_tracking_event(tracking_id: str, event: TrackingEvent):
    """Add tracking event (for testing)"""
    if tracking_id not in tracking_data:
        raise HTTPException(status_code=404, detail="Tracking ID not found")
    
    tracking_data[tracking_id].events.append(event)
    tracking_data[tracking_id].current_status = event.event_type
    
    return {"message": "Event added successfully"}
