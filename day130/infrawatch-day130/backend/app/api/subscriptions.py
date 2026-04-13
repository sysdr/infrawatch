from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.models import PushSubscription, User, NotificationPreference
from app.schemas.schemas import PushSubscriptionCreate, PushSubscriptionOut
import uuid, logging
from datetime import datetime, timezone

router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])
logger = logging.getLogger(__name__)

def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)

@router.post("", response_model=PushSubscriptionOut)
async def create_subscription(data: PushSubscriptionCreate, db: AsyncSession = Depends(get_db)):
    user = (await db.execute(select(User).where(User.id == data.user_id))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    sub = (await db.execute(select(PushSubscription).where(PushSubscription.endpoint == data.endpoint))).scalar_one_or_none()
    if sub:
        sub.is_active = True; sub.p256dh = data.keys.p256dh; sub.auth = data.keys.auth; sub.last_used = utcnow()
    else:
        sub = PushSubscription(id=str(uuid.uuid4()), user_id=data.user_id, endpoint=data.endpoint,
                               p256dh=data.keys.p256dh, auth=data.keys.auth, user_agent=data.user_agent)
        db.add(sub)

    if not (await db.execute(select(NotificationPreference).where(NotificationPreference.user_id == data.user_id))).scalar_one_or_none():
        defaults = {
            "devops":  dict(alerts_enabled=True,  team_updates_enabled=True,  daily_digest_enabled=True,  security_events_enabled=True),
            "manager": dict(alerts_enabled=False, team_updates_enabled=True,  daily_digest_enabled=True,  security_events_enabled=False),
        }.get(user.role, dict(alerts_enabled=True, team_updates_enabled=True, daily_digest_enabled=True, security_events_enabled=True))
        db.add(NotificationPreference(id=str(uuid.uuid4()), user_id=data.user_id, **defaults))

    await db.commit(); await db.refresh(sub)
    return sub

@router.get("/user/{user_id}")
async def get_user_subscriptions(user_id: str, db: AsyncSession = Depends(get_db)):
    subs = (await db.execute(select(PushSubscription).where(PushSubscription.user_id == user_id, PushSubscription.is_active == True))).scalars().all()
    return [{"id": s.id, "endpoint": s.endpoint[:50]+"...", "is_active": s.is_active, "created_at": s.created_at} for s in subs]

@router.delete("/{subscription_id}")
async def delete_subscription(subscription_id: str, db: AsyncSession = Depends(get_db)):
    sub = (await db.execute(select(PushSubscription).where(PushSubscription.id == subscription_id))).scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    sub.is_active = False; await db.commit()
    return {"status": "unsubscribed"}
