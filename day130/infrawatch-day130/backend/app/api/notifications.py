from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.models import Notification, NotificationEvent, NotificationPreference, PushSubscription, User
from app.schemas.schemas import (NotificationEventCreate, SendNotificationRequest,
                                  NotificationPreferenceUpdate, NotificationPreferenceOut, SnoozeRequest)
from app.services.push_service import send_web_push
import uuid, logging
from datetime import datetime, timezone, timedelta

router = APIRouter(prefix="/api/notifications", tags=["notifications"])
logger = logging.getLogger(__name__)

def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)

@router.post("/send")
async def send_notification(req: SendNotificationRequest, db: AsyncSession = Depends(get_db)):
    if not (await db.execute(select(User).where(User.id == req.user_id))).scalar_one_or_none():
        raise HTTPException(status_code=404, detail="User not found")

    subs   = (await db.execute(select(PushSubscription).where(PushSubscription.user_id == req.user_id, PushSubscription.is_active == True))).scalars().all()
    notif  = Notification(id=str(uuid.uuid4()), user_id=req.user_id, category=req.category,
                          title=req.title, body=req.body, url=req.url, status="sent")
    db.add(notif); await db.flush()

    results = []; now = utcnow()
    for sub in subs:
        ok = await send_web_push({"endpoint": sub.endpoint, "keys": {"p256dh": sub.p256dh, "auth": sub.auth}},
                                  {"title": req.title, "body": req.body, "icon": "/icons/icon-192x192.png", "url": req.url}, notif.id)
        if ok:
            notif.status = "delivered"; notif.delivered_at = now
            db.add(NotificationEvent(notification_id=notif.id, event_type="delivered"))
        elif not sub.endpoint.startswith("https://test"):
            sub.is_active = False
        results.append({"endpoint": sub.endpoint[:40]+"...", "sent": ok})

    await db.commit()
    return {"notification_id": notif.id, "results": results}

@router.post("/event")
async def record_event(event: NotificationEventCreate, db: AsyncSession = Depends(get_db)):
    notif = (await db.execute(select(Notification).where(Notification.id == event.notification_id))).scalar_one_or_none()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    now = utcnow()
    if event.event_type == "clicked":
        notif.clicked_at = now; notif.status = "clicked"
    elif event.event_type == "dismissed":
        notif.dismissed_at = now; notif.status = "dismissed"
    db.add(NotificationEvent(notification_id=event.notification_id, event_type=event.event_type))
    await db.commit()
    return {"status": "recorded"}

@router.get("/analytics")
async def get_analytics(db: AsyncSession = Depends(get_db)):
    total     = await db.scalar(select(func.count()).select_from(Notification))
    delivered = await db.scalar(select(func.count()).select_from(Notification).where(Notification.status.in_(["delivered","clicked","dismissed"])))
    clicked   = await db.scalar(select(func.count()).select_from(Notification).where(Notification.status == "clicked"))
    dismissed = await db.scalar(select(func.count()).select_from(Notification).where(Notification.status == "dismissed"))
    failed    = await db.scalar(select(func.count()).select_from(Notification).where(Notification.status == "failed"))
    act_subs  = await db.scalar(select(func.count()).select_from(PushSubscription).where(PushSubscription.is_active == True))
    ina_subs  = await db.scalar(select(func.count()).select_from(PushSubscription).where(PushSubscription.is_active == False))

    by_cat  = [{"category": r.category, "count": r.count} for r in (await db.execute(
        select(Notification.category, func.count().label("count")).group_by(Notification.category)))]
    recent  = [{"id": n.id, "title": n.title, "category": n.category, "status": n.status,
                "sent_at": n.sent_at.isoformat() if n.sent_at else None}
               for n in (await db.execute(select(Notification).order_by(Notification.sent_at.desc()).limit(10))).scalars().all()]

    return {
        "totals": {"sent": total, "delivered": delivered, "clicked": clicked, "dismissed": dismissed, "failed": failed},
        "rates": {
            "delivery_rate": round((delivered/total*100) if total else 0, 1),
            "ctr":           round((clicked/delivered*100) if delivered else 0, 1),
            "dismiss_rate":  round((dismissed/delivered*100) if delivered else 0, 1),
        },
        "subscriptions": {"active": act_subs, "inactive": ina_subs},
        "by_category": by_cat,
        "recent": recent,
    }

@router.get("/preferences/{user_id}", response_model=NotificationPreferenceOut)
async def get_preferences(user_id: str, db: AsyncSession = Depends(get_db)):
    pref = (await db.execute(select(NotificationPreference).where(NotificationPreference.user_id == user_id))).scalar_one_or_none()
    if not pref:
        raise HTTPException(status_code=404, detail="Preferences not found")
    return pref

@router.patch("/preferences/{user_id}", response_model=NotificationPreferenceOut)
async def update_preferences(user_id: str, update: NotificationPreferenceUpdate, db: AsyncSession = Depends(get_db)):
    pref = (await db.execute(select(NotificationPreference).where(NotificationPreference.user_id == user_id))).scalar_one_or_none()
    if not pref:
        raise HTTPException(status_code=404, detail="Preferences not found — subscribe first")
    for field, value in update.model_dump(exclude_none=True).items():
        setattr(pref, field, value)
    await db.commit(); await db.refresh(pref)
    return pref

@router.post("/snooze")
async def snooze_notifications(req: SnoozeRequest, db: AsyncSession = Depends(get_db)):
    pref = (await db.execute(select(NotificationPreference).where(NotificationPreference.user_id == req.user_id))).scalar_one_or_none()
    if not pref:
        raise HTTPException(status_code=404, detail="Preferences not found")
    pref.snoozed_until = utcnow() + timedelta(minutes=req.duration_minutes)
    await db.commit()
    return {"snoozed_until": pref.snoozed_until.isoformat()}

@router.delete("/snooze/{user_id}")
async def clear_snooze(user_id: str, db: AsyncSession = Depends(get_db)):
    pref = (await db.execute(select(NotificationPreference).where(NotificationPreference.user_id == user_id))).scalar_one_or_none()
    if not pref:
        raise HTTPException(status_code=404, detail="Preferences not found")
    pref.snoozed_until = None
    await db.commit()
    return {"status": "snooze cleared"}
