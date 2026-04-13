import logging
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

async def _heartbeat_check():
    """Every 60s: send alert notifications to eligible subscribers."""
    from app.database import get_session_factory
    from app.models.models import User, PushSubscription, NotificationPreference, Notification, NotificationEvent
    from app.services.push_service import send_web_push
    from sqlalchemy import select
    import uuid

    factory = get_session_factory()
    async with factory() as db:
        now  = datetime.now(timezone.utc).replace(tzinfo=None)
        hour = datetime.utcnow().hour

        result = await db.execute(select(User).join(PushSubscription, PushSubscription.user_id == User.id))
        users  = result.scalars().unique().all()

        for user in users:
            pref = (await db.execute(select(NotificationPreference).where(NotificationPreference.user_id == user.id))).scalar_one_or_none()
            if not pref or not pref.alerts_enabled:
                continue

            # Overnight-aware quiet hours check (e.g. 22–07)
            if pref.quiet_hours_enabled:
                s, e = pref.quiet_hours_start, pref.quiet_hours_end
                if (s > e and (hour >= s or hour < e)) or (s <= e and s <= hour < e):
                    continue

            if pref.snoozed_until and pref.snoozed_until > now:
                continue

            subs = (await db.execute(
                select(PushSubscription).where(PushSubscription.user_id == user.id, PushSubscription.is_active == True)
            )).scalars().all()
            if not subs:
                continue

            notif = Notification(
                id=str(uuid.uuid4()), user_id=user.id, category="alerts",
                title="⚡ InfraWatch Alert", body="CPU spike on prod-web-01 — 94%",
                url="/dashboard/alerts", status="sent"
            )
            db.add(notif)
            await db.flush()

            for sub in subs:
                ok = await send_web_push(
                    {"endpoint": sub.endpoint, "keys": {"p256dh": sub.p256dh, "auth": sub.auth}},
                    {"title": notif.title, "body": notif.body, "icon": "/icons/icon-192x192.png",
                     "url": notif.url, "tag": f"alert-{user.id}"},
                    notif.id
                )
                if ok:
                    notif.status = "delivered"; notif.delivered_at = now
                    db.add(NotificationEvent(notification_id=notif.id, event_type="delivered"))
                else:
                    notif.status = "failed"

        await db.commit()
    logger.debug("Heartbeat check complete")

async def _subscription_gc():
    """Nightly: purge inactive subscriptions."""
    from app.database import get_session_factory
    from app.models.models import PushSubscription
    from sqlalchemy import select

    factory = get_session_factory()
    async with factory() as db:
        stale = (await db.execute(select(PushSubscription).where(PushSubscription.is_active == False))).scalars().all()
        for s in stale:
            await db.delete(s)
        await db.commit()
    logger.info("GC removed %d stale subscriptions", len(stale))

def start_scheduler():
    scheduler.add_job(_heartbeat_check,  IntervalTrigger(seconds=60),       id="heartbeat",  replace_existing=True, misfire_grace_time=30)
    scheduler.add_job(_subscription_gc,  CronTrigger(hour=3, minute=0),     id="sub_gc",     replace_existing=True)
    if not scheduler.running:
        scheduler.start()
    logger.info("Scheduler started")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
