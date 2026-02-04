from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime, timedelta
import json

from models.alert import Alert
from utils.redis_client import get_redis_client

router = APIRouter()

@router.get("/", response_model=List[Alert])
async def get_alerts(
    active_only: bool = True,
    limit: int = 100
):
    redis = await get_redis_client()

    alert_keys = await redis.keys("alert:*")
    alerts = []

    for key in alert_keys[:limit]:
        alert_data = await redis.get(key)
        if alert_data:
            alert = json.loads(alert_data)
            if active_only and alert.get("resolved"):
                continue
            alerts.append(alert)

    return alerts

@router.post("/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    redis = await get_redis_client()

    key = f"alert:{alert_id}"
    alert_data = await redis.get(key)

    if not alert_data:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert = json.loads(alert_data)
    alert["resolved"] = True
    alert["resolved_at"] = datetime.utcnow().isoformat()

    await redis.set(key, json.dumps(alert))

    return {"status": "resolved", "alert_id": alert_id}
