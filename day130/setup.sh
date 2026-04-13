#!/usr/bin/env bash
# =============================================================================
# Day 130: Push Notifications — InfraWatch
# setup.sh — full project creation, build, test, and demo
# Usage:
#   ./setup.sh                  # run without Docker
#   USE_DOCKER=true ./setup.sh  # run with Docker
#   ./setup.sh stop             # stop all services
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR/infrawatch-day130"
USE_DOCKER="${USE_DOCKER:-false}"
BACKEND_PORT=8130
FRONTEND_PORT=3130

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
info()    { echo -e "${CYAN}[INFO]${NC} $*"; }
success() { echo -e "${GREEN}[OK]${NC}   $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $*"; }
error()   { echo -e "${RED}[ERR]${NC}  $*"; exit 1; }

# ── STOP ─────────────────────────────────────────────────────────────────────
if [[ "${1:-}" == "stop" ]]; then
  info "Stopping services..."
  pkill -f "uvicorn.*8130" 2>/dev/null || true
  pkill -f "vite.*3130"    2>/dev/null || true
  if [[ "$USE_DOCKER" == "true" ]]; then
    cd "$PROJECT_DIR" 2>/dev/null && docker compose down -v 2>/dev/null || true
  fi
  success "All services stopped."
  exit 0
fi

# ── PREFLIGHT ────────────────────────────────────────────────────────────────
info "Day 130: Push Notifications — InfraWatch"
info "Project dir: $PROJECT_DIR"

command -v python3 >/dev/null || error "python3 required"
command -v node    >/dev/null || error "node required"
command -v npm     >/dev/null || error "npm required"

if [[ "$USE_DOCKER" == "true" ]]; then
  command -v docker >/dev/null || error "docker required"
  docker compose version >/dev/null 2>&1 || error "docker compose required"
fi

# ── PROJECT STRUCTURE ────────────────────────────────────────────────────────
info "Creating project structure..."
mkdir -p "$PROJECT_DIR/backend/app/api"
mkdir -p "$PROJECT_DIR/backend/app/models"
mkdir -p "$PROJECT_DIR/backend/app/services"
mkdir -p "$PROJECT_DIR/backend/app/schemas"
mkdir -p "$PROJECT_DIR/backend/tests"
mkdir -p "$PROJECT_DIR/frontend/src/components"
mkdir -p "$PROJECT_DIR/frontend/src/hooks"
mkdir -p "$PROJECT_DIR/frontend/src/services"
mkdir -p "$PROJECT_DIR/frontend/src/pages"
mkdir -p "$PROJECT_DIR/frontend/public/icons"

# ── BACKEND FILES ────────────────────────────────────────────────────────────
info "Writing backend source files..."

cat > "$PROJECT_DIR/backend/requirements.txt" << 'REQEOF'
fastapi==0.115.5
uvicorn[standard]==0.32.1
sqlalchemy==2.0.36
aiosqlite==0.20.0
alembic==1.14.0
pydantic==2.10.3
pydantic-settings==2.7.0
apscheduler==3.10.4
pywebpush==2.0.0
cryptography==43.0.3
httpx==0.28.1
pytest==8.3.4
pytest-asyncio==0.24.0
anyio==4.7.0
python-multipart==0.0.20
pytz==2024.2
REQEOF

cat > "$PROJECT_DIR/backend/.env" << 'ENVEOF'
DATABASE_URL=sqlite+aiosqlite:///./infrawatch.db
VAPID_PRIVATE_KEY=
VAPID_PUBLIC_KEY=
VAPID_CLAIMS_EMAIL=mailto:admin@infrawatch.dev
SECRET_KEY=
ENVIRONMENT=development
ENVEOF

cat > "$PROJECT_DIR/backend/generate_vapid.py" << 'VAPIDGEN'
#!/usr/bin/env python3
"""Generate VAPID EC P-256 keys and write them to .env"""
import base64, os, re
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend

private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
public_key  = private_key.public_key()

private_bytes = private_key.private_numbers().private_value.to_bytes(32, 'big')
private_b64   = base64.urlsafe_b64encode(private_bytes).rstrip(b'=').decode()

pub_nums     = public_key.public_numbers()
public_bytes = b'\x04' + pub_nums.x.to_bytes(32,'big') + pub_nums.y.to_bytes(32,'big')
public_b64   = base64.urlsafe_b64encode(public_bytes).rstrip(b'=').decode()

env_path = os.path.join(os.path.dirname(__file__), '.env')
with open(env_path, 'r') as f:
    content = f.read()
content = re.sub(r'^VAPID_PRIVATE_KEY=.*$', f'VAPID_PRIVATE_KEY={private_b64}', content, flags=re.MULTILINE)
content = re.sub(r'^VAPID_PUBLIC_KEY=.*$',  f'VAPID_PUBLIC_KEY={public_b64}',   content, flags=re.MULTILINE)
with open(env_path, 'w') as f:
    f.write(content)
print(f"VAPID_PUBLIC_KEY={public_b64}")
print(f"VAPID_PRIVATE_KEY={private_b64[:12]}...")
print("Keys written to .env")
VAPIDGEN

touch "$PROJECT_DIR/backend/app/__init__.py"

cat > "$PROJECT_DIR/backend/app/config.py" << 'CFGEOF'
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./infrawatch.db"
    VAPID_PRIVATE_KEY: str = ""
    VAPID_PUBLIC_KEY: str = ""
    VAPID_CLAIMS_EMAIL: str = "mailto:admin@infrawatch.dev"
    SECRET_KEY: str = "infrawatch-day130"
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()
CFGEOF

cat > "$PROJECT_DIR/backend/app/database.py" << 'DBEOF'
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import get_settings

class Base(DeclarativeBase):
    pass

_engine = None
_SessionLocal = None

def get_engine():
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(settings.DATABASE_URL, echo=False)
    return _engine

def get_session_factory():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = async_sessionmaker(get_engine(), expire_on_commit=False)
    return _SessionLocal

async def init_db():
    from app.models.models import Base as M
    async with get_engine().begin() as conn:
        await conn.run_sync(M.metadata.create_all)

async def get_db():
    factory = get_session_factory()
    async with factory() as session:
        yield session
DBEOF

touch "$PROJECT_DIR/backend/app/models/__init__.py"

cat > "$PROJECT_DIR/backend/app/models/models.py" << 'MODEOF'
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from app.database import Base

def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)

class User(Base):
    __tablename__ = "users"
    id         = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username   = Column(String(50), unique=True, nullable=False)
    email      = Column(String(100), unique=True, nullable=False)
    role       = Column(String(20), default="engineer")
    timezone   = Column(String(50), default="UTC")
    created_at = Column(DateTime, default=utcnow)
    subscriptions = relationship("PushSubscription",       back_populates="user", cascade="all, delete-orphan")
    preferences   = relationship("NotificationPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")

class PushSubscription(Base):
    __tablename__ = "push_subscriptions"
    id         = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id    = Column(String, ForeignKey("users.id"), nullable=False)
    endpoint   = Column(Text, nullable=False)
    p256dh     = Column(Text, nullable=False)
    auth       = Column(Text, nullable=False)
    user_agent = Column(String(200))
    is_active  = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)
    last_used  = Column(DateTime)
    user       = relationship("User", back_populates="subscriptions")

class NotificationPreference(Base):
    __tablename__ = "notification_preferences"
    id                      = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id                 = Column(String, ForeignKey("users.id"), nullable=False, unique=True)
    alerts_enabled          = Column(Boolean, default=True)
    team_updates_enabled    = Column(Boolean, default=True)
    daily_digest_enabled    = Column(Boolean, default=True)
    security_events_enabled = Column(Boolean, default=True)
    quiet_hours_start       = Column(Integer, default=22)
    quiet_hours_end         = Column(Integer, default=8)
    quiet_hours_enabled     = Column(Boolean, default=False)
    snoozed_until           = Column(DateTime, nullable=True)
    updated_at              = Column(DateTime, default=utcnow, onupdate=utcnow)
    user                    = relationship("User", back_populates="preferences")

class Notification(Base):
    __tablename__ = "notifications"
    id           = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id      = Column(String, ForeignKey("users.id"), nullable=False)
    category     = Column(String(50), nullable=False)
    title        = Column(String(200), nullable=False)
    body         = Column(Text, nullable=False)
    url          = Column(String(500), default="/")
    sent_at      = Column(DateTime, default=utcnow)
    delivered_at = Column(DateTime)
    clicked_at   = Column(DateTime)
    dismissed_at = Column(DateTime)
    status       = Column(String(20), default="sent")
    extra_data   = Column(JSON, default=dict)

class NotificationEvent(Base):
    __tablename__    = "notification_events"
    id               = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    notification_id  = Column(String, ForeignKey("notifications.id"), nullable=False)
    event_type       = Column(String(30), nullable=False)
    occurred_at      = Column(DateTime, default=utcnow)
    event_metadata   = Column(JSON, default=dict)
MODEOF

touch "$PROJECT_DIR/backend/app/schemas/__init__.py"

cat > "$PROJECT_DIR/backend/app/schemas/schemas.py" << 'SCHEOF'
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SubscriptionKeys(BaseModel):
    p256dh: str
    auth: str

class PushSubscriptionCreate(BaseModel):
    user_id: str
    endpoint: str
    keys: SubscriptionKeys
    user_agent: Optional[str] = None

class PushSubscriptionOut(BaseModel):
    id: str
    user_id: str
    endpoint: str
    is_active: bool
    created_at: datetime
    model_config = {"from_attributes": True}

class NotificationPreferenceUpdate(BaseModel):
    alerts_enabled: Optional[bool] = None
    team_updates_enabled: Optional[bool] = None
    daily_digest_enabled: Optional[bool] = None
    security_events_enabled: Optional[bool] = None
    quiet_hours_start: Optional[int] = None
    quiet_hours_end: Optional[int] = None
    quiet_hours_enabled: Optional[bool] = None

class NotificationPreferenceOut(BaseModel):
    user_id: str
    alerts_enabled: bool
    team_updates_enabled: bool
    daily_digest_enabled: bool
    security_events_enabled: bool
    quiet_hours_start: int
    quiet_hours_end: int
    quiet_hours_enabled: bool
    snoozed_until: Optional[datetime] = None
    model_config = {"from_attributes": True}

class NotificationEventCreate(BaseModel):
    notification_id: str
    event_type: str

class UserCreate(BaseModel):
    username: str
    email: str
    role: str = "engineer"
    timezone: str = "UTC"

class UserOut(BaseModel):
    id: str
    username: str
    email: str
    role: str
    timezone: str
    created_at: datetime
    model_config = {"from_attributes": True}

class SendNotificationRequest(BaseModel):
    user_id: str
    category: str
    title: str
    body: str
    url: str = "/"

class SnoozeRequest(BaseModel):
    user_id: str
    duration_minutes: int
SCHEOF

touch "$PROJECT_DIR/backend/app/services/__init__.py"

cat > "$PROJECT_DIR/backend/app/services/push_service.py" << 'PSEOF'
import json, logging
from datetime import datetime, timezone
from pywebpush import webpush, WebPushException
from app.config import get_settings

logger = logging.getLogger(__name__)

def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)

async def send_web_push(subscription_info: dict, payload: dict, notification_id: str) -> bool:
    """Send a Web Push notification using VAPID. Returns True on success."""
    settings = get_settings()
    if not settings.VAPID_PRIVATE_KEY or not settings.VAPID_PUBLIC_KEY:
        logger.warning("VAPID keys not configured; skipping push")
        return False
    try:
        data = {**payload, "id": notification_id}
        webpush(
            subscription_info=subscription_info,
            data=json.dumps(data),
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims={
                "sub": settings.VAPID_CLAIMS_EMAIL,
                "aud": _extract_audience(subscription_info["endpoint"]),
            },
        )
        return True
    except WebPushException as e:
        status = e.response.status_code if e.response is not None else 0
        if status == 410:
            logger.info("Subscription expired (410): %s", subscription_info.get("endpoint","?")[:60])
        elif status == 429:
            logger.warning("Rate limited (429) by push service")
        else:
            logger.error("WebPush error %s: %s", status, str(e))
        return False
    except Exception as e:
        logger.error("Unexpected push error: %s", str(e))
        return False

def _extract_audience(endpoint: str) -> str:
    from urllib.parse import urlparse
    p = urlparse(endpoint)
    return f"{p.scheme}://{p.netloc}"
PSEOF

cat > "$PROJECT_DIR/backend/app/services/scheduler_service.py" << 'SCHEDEOF'
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
SCHEDEOF

touch "$PROJECT_DIR/backend/app/api/__init__.py"

cat > "$PROJECT_DIR/backend/app/api/subscriptions.py" << 'SUBEOF'
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
SUBEOF

cat > "$PROJECT_DIR/backend/app/api/notifications.py" << 'NOTIFEOF'
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
NOTIFEOF

cat > "$PROJECT_DIR/backend/app/api/users.py" << 'USEREOF'
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.models import User
from app.schemas.schemas import UserCreate, UserOut
import uuid

router = APIRouter(prefix="/api/users", tags=["users"])

@router.post("", response_model=UserOut)
async def create_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    if (await db.execute(select(User).where(User.username == data.username))).scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Username already exists")
    user = User(id=str(uuid.uuid4()), **data.model_dump())
    db.add(user); await db.commit(); await db.refresh(user)
    return user

@router.get("", response_model=list[UserOut])
async def list_users(db: AsyncSession = Depends(get_db)):
    return (await db.execute(select(User))).scalars().all()

@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
USEREOF

cat > "$PROJECT_DIR/backend/app/api/vapid.py" << 'VAPEOF'
from fastapi import APIRouter
from app.config import get_settings

router = APIRouter(prefix="/api/vapid", tags=["vapid"])

@router.get("/public-key")
async def get_vapid_public_key():
    return {"public_key": get_settings().VAPID_PUBLIC_KEY}
VAPEOF

cat > "$PROJECT_DIR/backend/main.py" << 'MAINEOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import init_db
from app.api import subscriptions, notifications, users, vapid
from app.services.scheduler_service import start_scheduler, stop_scheduler
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    start_scheduler()
    yield
    stop_scheduler()

app = FastAPI(title="InfraWatch Push Notifications API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware,
    allow_origins=["http://localhost:3130","http://localhost:5173","http://localhost:3000"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(subscriptions.router)
app.include_router(notifications.router)
app.include_router(users.router)
app.include_router(vapid.router)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "infrawatch-push-notifications", "day": 130}
MAINEOF

# ── TESTS ─────────────────────────────────────────────────────────────────────
info "Writing tests..."

touch "$PROJECT_DIR/backend/tests/__init__.py"

cat > "$PROJECT_DIR/backend/tests/conftest.py" << 'CONFEOF'
import pytest, pytest_asyncio, os
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.database import get_db

TEST_DB_URL = "sqlite+aiosqlite:///./test_infrawatch.db"

@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    from app.models.models import Base as M
    async with engine.begin() as conn:
        await conn.run_sync(M.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(M.metadata.drop_all)
    await engine.dispose()
    if os.path.exists("test_infrawatch.db"):
        os.remove("test_infrawatch.db")

@pytest_asyncio.fixture
async def db_session(test_engine):
    factory = async_sessionmaker(test_engine, expire_on_commit=False)
    async with factory() as session:
        yield session
        await session.rollback()

@pytest_asyncio.fixture
async def client(test_engine, db_session):
    from main import app
    factory = async_sessionmaker(test_engine, expire_on_commit=False)
    async def override_get_db():
        async with factory() as session:
            yield session
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
CONFEOF

cat > "$PROJECT_DIR/backend/tests/test_push_notifications.py" << 'TESTEOF'
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio(loop_scope="session")

KEYS = {"p256dh": "BNcRdreALRFXTkOOUHK1EtK2wtBYALTNFY5K9vZdQZfVpL6mZ7TsRIb7A-aGNlrOJEWlYRnbP8Ep8k9bG9B3T1E=",
        "auth":   "tBHItJI5svbpez7KI4CCXg=="}

async def _make_user(client, username, email, role="devops"):
    r = await client.post("/api/users", json={"username": username, "email": email, "role": role})
    assert r.status_code == 200
    return r.json()["id"]

async def _make_sub(client, user_id, endpoint):
    r = await client.post("/api/subscriptions", json={"user_id": user_id, "endpoint": endpoint, "keys": KEYS})
    assert r.status_code == 200
    return r.json()

async def test_create_user(client: AsyncClient):
    uid = await _make_user(client, "alice_devops", "alice@infrawatch.dev", "devops")
    assert uid

async def test_list_users(client: AsyncClient):
    r = await client.get("/api/users")
    assert r.status_code == 200 and isinstance(r.json(), list)

async def test_create_subscription(client: AsyncClient):
    uid = await _make_user(client, "bob_sre", "bob@infrawatch.dev")
    sub = await _make_sub(client, uid, "https://fcm.googleapis.com/fcm/send/test-001")
    assert sub["user_id"] == uid and sub["is_active"] is True

async def test_get_user_subscriptions(client: AsyncClient):
    uid = await _make_user(client, "carol_ops", "carol@infrawatch.dev", "engineer")
    await _make_sub(client, uid, "https://fcm.googleapis.com/fcm/send/test-carol")
    r = await client.get(f"/api/subscriptions/user/{uid}")
    assert r.status_code == 200 and len(r.json()) >= 1

async def test_get_and_update_preferences(client: AsyncClient):
    uid = await _make_user(client, "dave_pm", "dave@infrawatch.dev", "manager")
    await _make_sub(client, uid, "https://fcm.googleapis.com/fcm/send/test-dave")
    r = await client.get(f"/api/notifications/preferences/{uid}")
    assert r.status_code == 200 and r.json()["daily_digest_enabled"] is True

    r = await client.patch(f"/api/notifications/preferences/{uid}",
                           json={"quiet_hours_enabled": True, "quiet_hours_start": 23, "quiet_hours_end": 7})
    assert r.status_code == 200 and r.json()["quiet_hours_enabled"] is True and r.json()["quiet_hours_start"] == 23

async def test_analytics_endpoint(client: AsyncClient):
    r = await client.get("/api/notifications/analytics")
    assert r.status_code == 200
    d = r.json()
    assert "totals" in d and "rates" in d and "delivery_rate" in d["rates"]

async def test_record_notification_event(client: AsyncClient):
    uid = await _make_user(client, "eve_sre", "eve@infrawatch.dev")
    await _make_sub(client, uid, "https://test.fcm.invalid/test-eve")

    send = await client.post("/api/notifications/send",
                             json={"user_id": uid, "category": "alerts", "title": "Test", "body": "CPU 95%", "url": "/dashboard"})
    assert send.status_code == 200
    nid = send.json()["notification_id"]

    r = await client.post("/api/notifications/event", json={"notification_id": nid, "event_type": "clicked"})
    assert r.status_code == 200

    a = (await client.get("/api/notifications/analytics")).json()
    assert a["totals"]["clicked"] >= 1

async def test_snooze_and_clear(client: AsyncClient):
    uid = await _make_user(client, "frank_oncall", "frank@infrawatch.dev")
    await _make_sub(client, uid, "https://fcm.googleapis.com/fcm/send/test-frank")

    r = await client.post("/api/notifications/snooze", json={"user_id": uid, "duration_minutes": 60})
    assert r.status_code == 200 and "snoozed_until" in r.json()

    r = await client.delete(f"/api/notifications/snooze/{uid}")
    assert r.status_code == 200

async def test_vapid_public_key(client: AsyncClient):
    r = await client.get("/api/vapid/public-key")
    assert r.status_code == 200 and "public_key" in r.json()

async def test_health(client: AsyncClient):
    r = await client.get("/health")
    assert r.status_code == 200 and r.json()["day"] == 130
TESTEOF

cat > "$PROJECT_DIR/backend/pytest.ini" << 'PYTEOF'
[pytest]
asyncio_mode = auto
asyncio_default_fixture_loop_scope = session
testpaths = tests
PYTEOF

cat > "$PROJECT_DIR/backend/Dockerfile" << 'DKBEOF'
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python generate_vapid.py
EXPOSE 8130
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8130"]
DKBEOF

# ── FRONTEND ──────────────────────────────────────────────────────────────────
info "Writing frontend source files..."

cat > "$PROJECT_DIR/frontend/package.json" << 'PKGEOF'
{
  "name": "infrawatch-day130",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev":     "vite --port 3130 --host",
    "build":   "vite build",
    "preview": "vite preview --port 3130"
  },
  "dependencies": {
    "axios":      "^1.7.9",
    "recharts":   "^2.14.1",
    "react":      "^18.3.1",
    "react-dom":  "^18.3.1"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.4",
    "vite": "^6.0.7"
  }
}
PKGEOF

cat > "$PROJECT_DIR/frontend/vite.config.js" << 'VITEEOF'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3130, host: true,
    proxy: { '/api': { target: 'http://localhost:8130', changeOrigin: true } }
  }
})
VITEEOF

cat > "$PROJECT_DIR/frontend/index.html" << 'HTMLEOF'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>InfraWatch — Push Notifications</title>
  <link rel="manifest" href="/manifest.json"/>
  <meta name="theme-color" content="#0a1628"/>
  <style>* { margin:0; padding:0; box-sizing:border-box; } body { background:#0a1628; color:#e0e6f0; font-family:'Segoe UI',system-ui,sans-serif; }</style>
</head>
<body>
  <div id="root"></div>
  <script type="module" src="/src/main.jsx"></script>
</body>
</html>
HTMLEOF

cat > "$PROJECT_DIR/frontend/public/manifest.json" << 'MFEOF'
{"name":"InfraWatch","short_name":"InfraWatch","start_url":"/","display":"standalone",
 "background_color":"#0a1628","theme_color":"#0a1628",
 "icons":[{"src":"/icons/icon-192x192.png","sizes":"192x192","type":"image/png"}]}
MFEOF

# Minimal 1×1 PNG icon placeholders
python3 -c "
import base64, os
png = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==')
for n in ['icon-192x192.png','icon-512x512.png','badge-72x72.png']:
    open(os.path.join('$PROJECT_DIR/frontend/public/icons', n), 'wb').write(png)
print('Icons written')
"

cat > "$PROJECT_DIR/frontend/public/sw.js" << 'SWEOF'
/* InfraWatch Service Worker — Day 130 */
const CACHE = 'infrawatch-v130';
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(['/','/index.html']))); self.skipWaiting(); });
self.addEventListener('activate', e => { e.waitUntil(self.clients.claim()); });

self.addEventListener('push', event => {
  let d = {};
  try { d = event.data ? event.data.json() : {}; } catch(e) { d = {title:'InfraWatch',body:event.data?.text()||''}; }
  event.waitUntil(
    self.registration.showNotification(d.title||'InfraWatch', {
      body: d.body||'New notification', icon: d.icon||'/icons/icon-192x192.png',
      badge: '/icons/badge-72x72.png', tag: d.tag||'infrawatch', renotify: true,
      data: {url: d.url||'/', notificationId: d.id},
      actions: [{action:'view',title:'View Dashboard'},{action:'dismiss',title:'Dismiss'}]
    }).then(() => reportEvent(d.id,'delivered'))
  );
});

self.addEventListener('notificationclick', event => {
  const {notification:{data:nd={},close}, action} = event;
  notification.close();
  if (action === 'dismiss') { event.waitUntil(reportEvent(nd.notificationId,'dismissed')); return; }
  event.waitUntil(reportEvent(nd.notificationId,'clicked').then(() =>
    self.clients.matchAll({type:'window',includeUncontrolled:true}).then(cls => {
      for (const c of cls) if ('focus' in c) return c.focus();
      return self.clients.openWindow(nd.url||'/');
    })
  ));
});

self.addEventListener('notificationclose', event => {
  event.waitUntil(reportEvent((event.notification.data||{}).notificationId,'dismissed'));
});

async function reportEvent(id, type) {
  if (!id) return;
  try { await fetch('/api/notifications/event',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({notification_id:id,event_type:type})}); } catch(_) {}
}

self.addEventListener('fetch', event => {
  if (event.request.url.includes('/api/')) {
    event.respondWith(fetch(event.request).catch(()=>new Response('{"error":"offline"}',{headers:{'Content-Type':'application/json'}})));
    return;
  }
  event.respondWith(caches.match(event.request).then(c => c || fetch(event.request)));
});
SWEOF

cat > "$PROJECT_DIR/frontend/src/main.jsx" << 'MAINEOF'
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () =>
    navigator.serviceWorker.register('/sw.js')
      .then(r => console.log('[SW] Registered:', r.scope))
      .catch(e => console.warn('[SW] Failed:', e))
  );
}
ReactDOM.createRoot(document.getElementById('root')).render(<React.StrictMode><App /></React.StrictMode>)
MAINEOF

cat > "$PROJECT_DIR/frontend/src/App.jsx" << 'APPEOF'
import React from 'react';
import Dashboard from './pages/Dashboard.jsx';
import './styles.css';
export default function App() { return <div className="app"><Dashboard /></div>; }
APPEOF

cat > "$PROJECT_DIR/frontend/src/styles.css" << 'CSSEOF'
:root {
  --bg-primary:#0a1628; --bg-secondary:#0f1f3d; --bg-card:#132040; --bg-card-hover:#1a2a50;
  --border:#1e3a5f; --text-primary:#e0e6f0; --text-secondary:#8899bb; --text-muted:#4a5a7a;
  --accent:#00d4aa; --accent-dim:#00a882; --accent-glow:rgba(0,212,170,0.15);
  --warn:#f59e0b; --danger:#ef4444; --success:#22c55e; --info:#3b82f6;
  --radius:12px; --radius-sm:8px;
}
*{box-sizing:border-box;margin:0;padding:0;}
body{background:var(--bg-primary);color:var(--text-primary);font-family:'Segoe UI',system-ui,sans-serif;font-size:14px;line-height:1.6;}
.app{min-height:100vh;}
.layout{display:flex;min-height:100vh;}
.sidebar{width:220px;background:var(--bg-secondary);border-right:1px solid var(--border);flex-shrink:0;}
.main-content{flex:1;overflow-y:auto;}
.topbar{background:var(--bg-secondary);border-bottom:1px solid var(--border);padding:0 24px;height:56px;display:flex;align-items:center;justify-content:space-between;}
.topbar-brand{display:flex;align-items:center;gap:10px;font-size:16px;font-weight:700;color:var(--accent);}
.sidebar-logo{padding:20px 18px 10px;font-size:15px;font-weight:700;color:var(--accent);display:flex;align-items:center;gap:8px;border-bottom:1px solid var(--border);margin-bottom:8px;}
.nav-item{padding:10px 18px;cursor:pointer;display:flex;align-items:center;gap:10px;color:var(--text-secondary);transition:all .15s;font-size:13.5px;}
.nav-item:hover{background:var(--bg-card);color:var(--text-primary);}
.nav-item.active{background:var(--accent-glow);color:var(--accent);border-right:2px solid var(--accent);}
.page{padding:24px;}
.page-title{font-size:20px;font-weight:700;color:var(--text-primary);margin-bottom:4px;}
.page-subtitle{color:var(--text-secondary);font-size:13px;margin-bottom:24px;}
.card{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);padding:20px;}
.card-title{font-size:13px;font-weight:600;color:var(--text-secondary);text-transform:uppercase;letter-spacing:.05em;margin-bottom:14px;}
.grid-4{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:24px;}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:24px;}
@media(max-width:1100px){.grid-4{grid-template-columns:repeat(2,1fr);}}
@media(max-width:700px){.grid-4,.grid-2{grid-template-columns:1fr;}}
.stat-card{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);padding:18px;}
.stat-label{font-size:11px;font-weight:600;color:var(--text-secondary);text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px;}
.stat-value{font-size:28px;font-weight:700;color:var(--text-primary);}
.stat-sub{font-size:12px;color:var(--text-muted);margin-top:4px;}
.stat-accent{color:var(--accent);}.stat-warn{color:var(--warn);}.stat-danger{color:var(--danger);}.stat-success{color:var(--success);}
.badge{display:inline-flex;align-items:center;padding:2px 8px;border-radius:20px;font-size:11px;font-weight:600;}
.badge-green{background:rgba(34,197,94,.15);color:var(--success);}
.badge-red{background:rgba(239,68,68,.15);color:var(--danger);}
.badge-yellow{background:rgba(245,158,11,.15);color:var(--warn);}
.badge-blue{background:rgba(59,130,246,.15);color:var(--info);}
.badge-teal{background:var(--accent-glow);color:var(--accent);}
.btn{display:inline-flex;align-items:center;gap:6px;padding:8px 16px;border-radius:var(--radius-sm);border:none;cursor:pointer;font-size:13px;font-weight:600;transition:all .15s;}
.btn-primary{background:var(--accent);color:#0a1628;}.btn-primary:hover{background:var(--accent-dim);}
.btn-secondary{background:var(--bg-card-hover);color:var(--text-primary);border:1px solid var(--border);}.btn-secondary:hover{border-color:var(--accent);color:var(--accent);}
.btn-danger{background:rgba(239,68,68,.15);color:var(--danger);border:1px solid rgba(239,68,68,.3);}.btn-danger:hover{background:rgba(239,68,68,.25);}
.btn-sm{padding:5px 10px;font-size:12px;}.btn:disabled{opacity:.45;cursor:not-allowed;}
.table-wrap{overflow-x:auto;}
table{width:100%;border-collapse:collapse;font-size:13px;}
th{padding:10px 12px;text-align:left;color:var(--text-muted);font-size:11px;text-transform:uppercase;letter-spacing:.05em;border-bottom:1px solid var(--border);}
td{padding:10px 12px;border-bottom:1px solid rgba(30,58,95,.5);color:var(--text-secondary);}
tr:hover td{background:var(--bg-card-hover);}tr:last-child td{border-bottom:none;}
.toggle{position:relative;display:inline-block;width:40px;height:22px;}
.toggle input{opacity:0;width:0;height:0;}
.toggle-slider{position:absolute;cursor:pointer;top:0;left:0;right:0;bottom:0;background:var(--text-muted);border-radius:22px;transition:.3s;}
.toggle-slider:before{position:absolute;content:"";height:16px;width:16px;left:3px;bottom:3px;background:white;border-radius:50%;transition:.3s;}
.toggle input:checked+.toggle-slider{background:var(--accent);}
.toggle input:checked+.toggle-slider:before{transform:translateX(18px);}
.pref-row{display:flex;align-items:center;justify-content:space-between;padding:12px 0;border-bottom:1px solid rgba(30,58,95,.4);}
.pref-row:last-child{border-bottom:none;}
.pref-info{display:flex;flex-direction:column;gap:2px;}
.pref-name{font-size:13.5px;font-weight:600;color:var(--text-primary);}
.pref-desc{font-size:12px;color:var(--text-muted);}
.subscribe-banner{background:linear-gradient(135deg,#0f2a4a,#0d3d2e);border:1px solid var(--accent);border-radius:var(--radius);padding:20px 24px;display:flex;align-items:center;justify-content:space-between;margin-bottom:24px;}
.subscribe-info h3{font-size:15px;font-weight:700;color:var(--accent);margin-bottom:4px;}
.subscribe-info p{font-size:13px;color:var(--text-secondary);}
.bar-row{display:flex;align-items:center;gap:10px;margin-bottom:8px;font-size:12px;}
.bar-label{width:100px;color:var(--text-secondary);text-align:right;font-size:12px;}
.bar-track{flex:1;background:var(--border);border-radius:4px;height:8px;overflow:hidden;}
.bar-fill{height:100%;border-radius:4px;background:var(--accent);transition:width .6s ease;}
.bar-val{width:36px;color:var(--text-primary);font-weight:600;text-align:right;}
.dot{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:6px;}
.dot-green{background:var(--success);}.dot-red{background:var(--danger);}.dot-yellow{background:var(--warn);}.dot-gray{background:var(--text-muted);}
.user-selector{background:var(--bg-card);border:1px solid var(--border);color:var(--text-primary);border-radius:var(--radius-sm);padding:6px 10px;font-size:13px;cursor:pointer;}
.user-selector:focus{outline:none;border-color:var(--accent);}
select option{background:var(--bg-card);}
.input{background:var(--bg-card);border:1px solid var(--border);color:var(--text-primary);border-radius:var(--radius-sm);padding:7px 12px;font-size:13px;width:100%;}
.input:focus{outline:none;border-color:var(--accent);}
.alert{padding:10px 14px;border-radius:var(--radius-sm);font-size:13px;margin-bottom:14px;}
.alert-info{background:rgba(59,130,246,.1);border:1px solid rgba(59,130,246,.3);color:#93c5fd;}
.alert-success{background:rgba(34,197,94,.1);border:1px solid rgba(34,197,94,.3);color:#86efac;}
.alert-warn{background:rgba(245,158,11,.1);border:1px solid rgba(245,158,11,.3);color:#fcd34d;}
.alert-error{background:rgba(239,68,68,.1);border:1px solid rgba(239,68,68,.3);color:#fca5a5;}
CSSEOF

cat > "$PROJECT_DIR/frontend/src/services/api.js" << 'APIEOF'
import axios from 'axios';
const API = axios.create({ baseURL: '/api', timeout: 10000 });
export const usersApi = {
  list: () => API.get('/users'),
  create: (d) => API.post('/users', d),
  get: (id) => API.get(`/users/${id}`),
};
export const vapidApi = {
  getPublicKey: () => API.get('/vapid/public-key'),
};
export const subscriptionsApi = {
  create: (d) => API.post('/subscriptions', d),
  getUserSubs: (uid) => API.get(`/subscriptions/user/${uid}`),
  delete: (id) => API.delete(`/subscriptions/${id}`),
};
export const notificationsApi = {
  send: (d) => API.post('/notifications/send', d),
  recordEvent: (d) => API.post('/notifications/event', d),
  getAnalytics: () => API.get('/notifications/analytics'),
  getPreferences: (uid) => API.get(`/notifications/preferences/${uid}`),
  updatePreferences: (uid, d) => API.patch(`/notifications/preferences/${uid}`, d),
  snooze: (d) => API.post('/notifications/snooze', d),
  clearSnooze: (uid) => API.delete(`/notifications/snooze/${uid}`),
};
APIEOF

cat > "$PROJECT_DIR/frontend/src/hooks/usePushNotifications.js" << 'HOOKEOF'
import { useState, useCallback } from 'react';
import { vapidApi, subscriptionsApi } from '../services/api.js';

function urlBase64ToUint8Array(b64) {
  const pad = '='.repeat((4 - b64.length % 4) % 4);
  const b = (b64 + pad).replace(/-/g, '+').replace(/_/g, '/');
  return Uint8Array.from([...window.atob(b)].map(c => c.charCodeAt(0)));
}

export function usePushNotifications() {
  const [status, setStatus] = useState('idle');
  const [error, setError] = useState(null);

  const subscribe = useCallback(async (userId) => {
    setStatus('requesting'); setError(null);
    try {
      if (!('Notification' in window))    throw new Error('Notifications not supported');
      if (!('serviceWorker' in navigator)) throw new Error('Service Worker not supported');
      if (!('PushManager' in window))      throw new Error('Push API not supported');

      const perm = await Notification.requestPermission();
      if (perm !== 'granted') { setStatus('denied'); return null; }

      const { data: vk } = await vapidApi.getPublicKey();
      if (!vk.public_key) throw new Error('VAPID public key not configured');

      const reg = await navigator.serviceWorker.ready;
      const ps  = await reg.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: urlBase64ToUint8Array(vk.public_key) });
      const sub = ps.toJSON();

      const { data } = await subscriptionsApi.create({
        user_id: userId, endpoint: sub.endpoint,
        keys: { p256dh: sub.keys.p256dh, auth: sub.keys.auth },
        user_agent: navigator.userAgent.slice(0, 200),
      });
      setStatus('subscribed');
      return data;
    } catch (err) { setStatus('error'); setError(err.message); return null; }
  }, []);

  const unsubscribe = useCallback(async (id) => {
    try { await subscriptionsApi.delete(id); setStatus('idle'); }
    catch (err) { setError(err.message); }
  }, []);

  const checkPermission = useCallback(() =>
    ('Notification' in window) ? Notification.permission : 'unsupported', []);

  return { status, error, subscribe, unsubscribe, checkPermission };
}
HOOKEOF

cat > "$PROJECT_DIR/frontend/src/pages/Dashboard.jsx" << 'DASHEOF'
import React, { useState, useEffect, useCallback } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, CartesianGrid } from 'recharts';
import { usersApi, notificationsApi, subscriptionsApi } from '../services/api.js';
import { usePushNotifications } from '../hooks/usePushNotifications.js';

const COLORS = ['#00d4aa','#3b82f6','#f59e0b','#ef4444','#a78bfa'];
const TT = { contentStyle:{background:'#132040',border:'1px solid #1e3a5f',borderRadius:8,fontSize:12} };

function Sidebar({ active, setActive }) {
  const items = [
    { id:'overview',     icon:'📊', label:'Overview'     },
    { id:'subscribe',    icon:'🔔', label:'Subscribe'    },
    { id:'preferences',  icon:'⚙️', label:'Preferences'  },
    { id:'send',         icon:'📤', label:'Send Test'    },
    { id:'analytics',    icon:'📈', label:'Analytics'    },
  ];
  return (
    <div className="sidebar">
      <div className="sidebar-logo">⚡ InfraWatch</div>
      <nav>
        {items.map(i => (
          <div key={i.id} className={`nav-item ${active===i.id?'active':''}`} onClick={()=>setActive(i.id)}>
            <span style={{fontSize:16}}>{i.icon}</span>{i.label}
          </div>
        ))}
      </nav>
    </div>
  );
}

function OverviewPage({ analytics }) {
  if (!analytics) return <div className="page"><p style={{color:'var(--text-secondary)'}}>Loading…</p></div>;
  const { totals:t, rates:r, subscriptions:s, by_category, recent } = analytics;
  return (
    <div className="page">
      <div className="page-title">Push Notification Overview</div>
      <div className="page-subtitle">Day 130 · Real-time delivery metrics and subscription health</div>
      <div className="grid-4">
        {[
          {label:'Total Sent',          val:t.sent,           cls:'',           sub:'all-time'},
          {label:'Delivery Rate',       val:r.delivery_rate+'%', cls:r.delivery_rate>=90?'stat-success':r.delivery_rate>=70?'stat-warn':'stat-danger', sub:t.delivered+' delivered'},
          {label:'Click-Through Rate',  val:r.ctr+'%',        cls:'stat-accent',sub:t.clicked+' clicked'},
          {label:'Active Subscriptions',val:s.active,         cls:'stat-success',sub:s.inactive+' inactive'},
        ].map(x=>(
          <div className="stat-card" key={x.label}>
            <div className="stat-label">{x.label}</div>
            <div className={`stat-value ${x.cls}`}>{x.val}</div>
            <div className="stat-sub">{x.sub}</div>
          </div>
        ))}
      </div>
      <div className="grid-2">
        <div className="card">
          <div className="card-title">Delivery Funnel</div>
          {[{label:'Sent',val:t.sent,color:'#3b82f6'},{label:'Delivered',val:t.delivered,color:'#00d4aa'},
            {label:'Clicked',val:t.clicked,color:'#22c55e'},{label:'Dismissed',val:t.dismissed,color:'#f59e0b'},
            {label:'Failed',val:t.failed,color:'#ef4444'}].map(row=>(
            <div className="bar-row" key={row.label}>
              <span className="bar-label">{row.label}</span>
              <div className="bar-track"><div className="bar-fill" style={{width:`${t.sent>0?Math.round(row.val/t.sent*100):0}%`,background:row.color}}/></div>
              <span className="bar-val">{row.val}</span>
            </div>
          ))}
        </div>
        <div className="card">
          <div className="card-title">By Category</div>
          {by_category.length===0
            ? <p style={{color:'var(--text-muted)',fontSize:13}}>No notifications yet — use Send Test tab.</p>
            : <ResponsiveContainer width="100%" height={180}>
                <PieChart><Pie data={by_category} dataKey="count" nameKey="category" cx="50%" cy="50%" outerRadius={70}
                    label={({category,percent})=>`${category} ${(percent*100).toFixed(0)}%`} labelLine={false}>
                  {by_category.map((_,i)=><Cell key={i} fill={COLORS[i%COLORS.length]}/>)}
                </Pie><Tooltip {...TT}/></PieChart>
              </ResponsiveContainer>
          }
        </div>
      </div>
      <div className="card">
        <div className="card-title">Recent Notifications</div>
        {recent.length===0
          ? <p style={{color:'var(--text-muted)',fontSize:13}}>No notifications yet.</p>
          : <div className="table-wrap"><table>
              <thead><tr><th>Title</th><th>Category</th><th>Status</th><th>Sent At</th></tr></thead>
              <tbody>{recent.map(n=>(
                <tr key={n.id}>
                  <td style={{color:'var(--text-primary)'}}>{n.title}</td>
                  <td><span className="badge badge-blue">{n.category}</span></td>
                  <td><span className={`badge ${n.status==='clicked'?'badge-green':n.status==='delivered'?'badge-teal':n.status==='failed'?'badge-red':'badge-yellow'}`}>{n.status}</span></td>
                  <td>{n.sent_at?new Date(n.sent_at).toLocaleString():'—'}</td>
                </tr>
              ))}</tbody>
            </table></div>
        }
      </div>
    </div>
  );
}

function SubscribePage({ users, refresh }) {
  const [sel, setSel] = useState('');
  const [subs, setSubs] = useState([]);
  const [msg, setMsg] = useState(null);
  const { status, error, subscribe, unsubscribe, checkPermission } = usePushNotifications();
  const perm = checkPermission();

  useEffect(()=>{ if(sel) subscriptionsApi.getUserSubs(sel).then(r=>setSubs(r.data)).catch(()=>setSubs([])); },[sel,status]);

  const handleSubscribe = async () => {
    if (!sel) return setMsg({type:'warn',text:'Select a user first'});
    const res = await subscribe(sel);
    if (res) { setMsg({type:'success',text:'Subscribed! Push enabled.'}); refresh(); }
    else if (error) setMsg({type:'error',text:error});
  };

  return (
    <div className="page">
      <div className="page-title">Subscription Management</div>
      <div className="page-subtitle">Enable Web Push for your browser session</div>
      {perm==='denied'&&<div className="alert alert-error" style={{marginBottom:16}}>🚫 Blocked — reset in Browser Settings → Site Settings → Notifications.</div>}
      <div className="subscribe-banner">
        <div className="subscribe-info">
          <h3>🔔 Enable Push Notifications</h3>
          <p>Instant alerts for CPU spikes, failures, and security events — even with the tab closed.</p>
        </div>
        <div style={{display:'flex',gap:10,alignItems:'center'}}>
          <select className="user-selector" value={sel} onChange={e=>setSel(e.target.value)}>
            <option value="">Select user…</option>
            {users.map(u=><option key={u.id} value={u.id}>{u.username} ({u.role})</option>)}
          </select>
          <button className="btn btn-primary" onClick={handleSubscribe} disabled={status==='requesting'||!sel}>
            {status==='requesting'?'⏳ Requesting…':status==='subscribed'?'✅ Re-Subscribe':'🔔 Subscribe'}
          </button>
        </div>
      </div>
      {msg&&<div className={`alert alert-${msg.type}`}>{msg.text}</div>}
      <div className="card">
        <div className="card-title">Active Subscriptions {sel?`— ${users.find(u=>u.id===sel)?.username}`:''}</div>
        {!sel ? <p style={{color:'var(--text-muted)',fontSize:13}}>Select a user to see subscriptions.</p>
          : subs.length===0 ? <p style={{color:'var(--text-muted)',fontSize:13}}>No active subscriptions. Click Subscribe above.</p>
          : <div className="table-wrap"><table>
              <thead><tr><th>Endpoint</th><th>Status</th><th>Created</th><th>Action</th></tr></thead>
              <tbody>{subs.map(s=>(
                <tr key={s.id}>
                  <td style={{fontFamily:'monospace',fontSize:11}}>{s.endpoint}</td>
                  <td><span className={`badge ${s.is_active?'badge-green':'badge-red'}`}>{s.is_active?'active':'inactive'}</span></td>
                  <td>{new Date(s.created_at).toLocaleString()}</td>
                  <td><button className="btn btn-danger btn-sm" onClick={()=>unsubscribe(s.id).then(()=>subscriptionsApi.getUserSubs(sel).then(r=>setSubs(r.data)))}>Unsubscribe</button></td>
                </tr>
              ))}</tbody>
            </table></div>
        }
      </div>
      <div className="card" style={{marginTop:16}}>
        <div className="card-title">Browser Capability Check</div>
        <div style={{display:'flex',gap:16,flexWrap:'wrap'}}>
          {[{label:'Notifications API',ok:'Notification'in window},{label:'Service Worker',ok:'serviceWorker'in navigator},
            {label:'Push Manager',ok:'PushManager'in window},{label:'Permission',ok:perm==='granted',warn:perm==='default'}].map(item=>(
            <div key={item.label} style={{background:'var(--bg-primary)',border:'1px solid var(--border)',borderRadius:8,padding:'10px 16px'}}>
              <span className={`dot ${item.ok?'dot-green':item.warn?'dot-yellow':'dot-red'}`}/>
              <span style={{fontSize:12,color:'var(--text-secondary)'}}>{item.label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function PreferencesPage({ users, refresh }) {
  const [sel, setSel] = useState('');
  const [prefs, setPrefs] = useState(null);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState(null);

  useEffect(()=>{ if(sel) notificationsApi.getPreferences(sel).then(r=>setPrefs(r.data)).catch(()=>setPrefs(null)); },[sel]);

  const toggle = async (field) => {
    if(!prefs) return;
    setPrefs({...prefs,[field]:!prefs[field]}); setSaving(true);
    await notificationsApi.updatePreferences(sel,{[field]:!prefs[field]}); setSaving(false);
    setMsg({type:'success',text:'Saved.'}); setTimeout(()=>setMsg(null),2000);
  };

  const handleSnooze = async (min) => {
    await notificationsApi.snooze({user_id:sel,duration_minutes:min});
    setPrefs((await notificationsApi.getPreferences(sel)).data);
    setMsg({type:'info',text:`Snoozed for ${min} min.`}); setTimeout(()=>setMsg(null),3000);
  };

  const clearSnooze = async () => {
    await notificationsApi.clearSnooze(sel);
    setPrefs((await notificationsApi.getPreferences(sel)).data);
    setMsg({type:'success',text:'Snooze cleared.'}); setTimeout(()=>setMsg(null),2000);
  };

  const items = prefs ? [
    {f:'alerts_enabled',          n:'⚡ Alert Notifications', d:'CPU spikes, memory, disk'},
    {f:'team_updates_enabled',    n:'👥 Team Updates',        d:'Members, roles, deployments'},
    {f:'daily_digest_enabled',    n:'📋 Daily Digest',        d:'Morning health summary (08:00)'},
    {f:'security_events_enabled', n:'🔒 Security Events',     d:'Failed logins, cert expiry'},
    {f:'quiet_hours_enabled',     n:`🌙 Quiet Hours (${prefs.quiet_hours_start}:00–${prefs.quiet_hours_end}:00)`, d:'Suppress non-critical at night'},
  ] : [];

  return (
    <div className="page">
      <div className="page-title">Notification Preferences</div>
      <div className="page-subtitle">Per-user, per-category controls with quiet hours and snooze</div>
      <div style={{marginBottom:20}}>
        <select className="user-selector" value={sel} onChange={e=>setSel(e.target.value)}>
          <option value="">Select user…</option>
          {users.map(u=><option key={u.id} value={u.id}>{u.username} ({u.role})</option>)}
        </select>
      </div>
      {msg&&<div className={`alert alert-${msg.type}`}>{msg.text}</div>}
      {!sel ? <div className="alert alert-info">Select a user to manage preferences.</div>
        : !prefs ? <div className="alert alert-warn">No preferences — subscribe this user first.</div>
        : <div className="grid-2">
            <div className="card">
              <div className="card-title">Category Controls {saving?'(saving…)':''}</div>
              {items.map(item=>(
                <div className="pref-row" key={item.f}>
                  <div className="pref-info"><span className="pref-name">{item.n}</span><span className="pref-desc">{item.d}</span></div>
                  <label className="toggle"><input type="checkbox" checked={!!prefs[item.f]} onChange={()=>toggle(item.f)}/><span className="toggle-slider"/></label>
                </div>
              ))}
            </div>
            <div className="card">
              <div className="card-title">Snooze Controls</div>
              {prefs.snoozed_until && new Date(prefs.snoozed_until)>new Date()
                ? <div><div className="alert alert-warn" style={{marginBottom:12}}>🔕 Snoozed until {new Date(prefs.snoozed_until).toLocaleString()}</div>
                    <button className="btn btn-secondary" onClick={clearSnooze}>Clear Snooze</button></div>
                : <div><p style={{color:'var(--text-muted)',fontSize:12,marginBottom:12}}>Temporarily suppress all non-critical</p>
                    <div style={{display:'flex',gap:8,flexWrap:'wrap'}}>
                      <button className="btn btn-secondary btn-sm" onClick={()=>handleSnooze(60)}>😴 1 Hour</button>
                      <button className="btn btn-secondary btn-sm" onClick={()=>handleSnooze(240)}>😴 4 Hours</button>
                      <button className="btn btn-secondary btn-sm" onClick={()=>handleSnooze(480)}>😴 8 Hours</button>
                    </div></div>
              }
              <div style={{marginTop:20}}>
                <div className="card-title">Role Defaults</div>
                {[{r:'devops',ok:true,n:'All categories on'},{r:'engineer',ok:true,n:'All categories on'},{r:'manager',ok:false,n:'Digest + team only'}].map(x=>(
                  <div key={x.r} style={{display:'flex',justifyContent:'space-between',padding:'6px 0',borderBottom:'1px solid var(--border)',fontSize:12}}>
                    <span style={{color:'var(--text-secondary)'}}>{x.r}</span>
                    <span style={{color:x.ok?'var(--success)':'var(--warn)'}}>{x.n}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
      }
    </div>
  );
}

function SendTestPage({ users, refresh }) {
  const [form, setForm] = useState({user_id:'',category:'alerts',title:'⚡ CPU Spike Detected',body:'prod-web-01 CPU at 94% — threshold exceeded',url:'/dashboard/alerts'});
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const send = async () => {
    if(!form.user_id) return setResult({type:'warn',text:'Select a user first'});
    setLoading(true); setResult(null);
    try {
      const {data} = await notificationsApi.send(form);
      setResult({type:'success',text:`Sent ✓ ID: ${data.notification_id.slice(0,12)}... Results: ${JSON.stringify(data.results)}`});
      refresh();
    } catch(e){ setResult({type:'error',text:e.response?.data?.detail||e.message}); }
    setLoading(false);
  };

  return (
    <div className="page">
      <div className="page-title">Send Test Notification</div>
      <div className="page-subtitle">Manually trigger a push for demo and debugging</div>
      <div className="card" style={{maxWidth:560}}>
        <div className="card-title">Notification Payload</div>
        <div style={{display:'flex',flexDirection:'column',gap:12}}>
          <div>
            <label style={{fontSize:11,color:'var(--text-muted)',display:'block',marginBottom:4}}>RECIPIENT</label>
            <select className="user-selector input" value={form.user_id} onChange={e=>setForm({...form,user_id:e.target.value})}>
              <option value="">Select user…</option>
              {users.map(u=><option key={u.id} value={u.id}>{u.username} ({u.role})</option>)}
            </select>
          </div>
          <div>
            <label style={{fontSize:11,color:'var(--text-muted)',display:'block',marginBottom:4}}>CATEGORY</label>
            <select className="user-selector input" value={form.category} onChange={e=>setForm({...form,category:e.target.value})}>
              <option value="alerts">⚡ Alerts</option>
              <option value="team_updates">👥 Team Updates</option>
              <option value="daily_digest">📋 Daily Digest</option>
              <option value="security_events">🔒 Security Events</option>
            </select>
          </div>
          {['title','body','url'].map(f=>(
            <div key={f}>
              <label style={{fontSize:11,color:'var(--text-muted)',display:'block',marginBottom:4}}>{f.toUpperCase()}</label>
              <input className="input" value={form[f]} onChange={e=>setForm({...form,[f]:e.target.value})}/>
            </div>
          ))}
          <button className="btn btn-primary" onClick={send} disabled={loading}>{loading?'⏳ Sending…':'📤 Send Notification'}</button>
        </div>
        {result&&<div className={`alert alert-${result.type}`} style={{marginTop:14,wordBreak:'break-all',fontSize:12}}>{result.text}</div>}
      </div>
      <div className="card" style={{marginTop:20,maxWidth:560}}>
        <div className="card-title">⚡ Quick Templates</div>
        {[
          {title:'🔴 Critical: Service Down',  body:'api-gateway-prod not responding — 5xx rate 100%',   category:'alerts'},
          {title:'🔐 Security: Login Anomaly', body:'15 failed logins from 185.220.x.x in last 5 min',  category:'security_events'},
          {title:'📋 Daily Digest',            body:'System health: 98% uptime · 3 alerts resolved',     category:'daily_digest'},
        ].map((t,i)=>(
          <div key={i} style={{padding:'10px 0',borderBottom:'1px solid var(--border)',cursor:'pointer'}} onClick={()=>setForm({...form,...t})}>
            <div style={{fontSize:13,fontWeight:600,color:'var(--text-primary)'}}>{t.title}</div>
            <div style={{fontSize:11,color:'var(--text-muted)',marginTop:2}}>{t.body}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function AnalyticsPage({ analytics }) {
  if (!analytics) return <div className="page"><p style={{color:'var(--text-secondary)'}}>Loading…</p></div>;
  const { totals:t, rates:r, subscriptions:s, by_category } = analytics;
  const funnel = [{name:'Sent',value:t.sent},{name:'Delivered',value:t.delivered},{name:'Clicked',value:t.clicked},{name:'Dismissed',value:t.dismissed}];
  return (
    <div className="page">
      <div className="page-title">Notification Analytics</div>
      <div className="page-subtitle">Delivery rates, engagement metrics, and subscription health</div>
      <div className="grid-4">
        {[
          {label:'Delivery Rate',      val:r.delivery_rate+'%', cls:r.delivery_rate>=90?'stat-success':'stat-warn', sub:'target ≥ 95%'},
          {label:'Click-Through Rate', val:r.ctr+'%',           cls:'stat-accent',  sub:'benchmark 10–20%'},
          {label:'Dismiss Rate',       val:r.dismiss_rate+'%',  cls:r.dismiss_rate<30?'stat-success':'stat-warn', sub:'high → reduce noise'},
          {label:'Active Subs',        val:s.active,            cls:'stat-success', sub:s.inactive+' inactive'},
        ].map(x=>(
          <div className="stat-card" key={x.label}>
            <div className="stat-label">{x.label}</div>
            <div className={`stat-value ${x.cls}`}>{x.val}</div>
            <div className="stat-sub">{x.sub}</div>
          </div>
        ))}
      </div>
      <div className="grid-2">
        <div className="card">
          <div className="card-title">Delivery Funnel</div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={funnel} margin={{top:4,right:20,bottom:0,left:0}}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e3a5f"/>
              <XAxis dataKey="name" tick={{fill:'#8899bb',fontSize:11}}/>
              <YAxis tick={{fill:'#8899bb',fontSize:11}} allowDecimals={false}/>
              <Tooltip {...TT}/><Bar dataKey="value" fill="#00d4aa" radius={[4,4,0,0]}/>
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="card">
          <div className="card-title">By Category</div>
          {by_category.length===0
            ? <p style={{color:'var(--text-muted)',fontSize:13}}>Send notifications first.</p>
            : <ResponsiveContainer width="100%" height={200}>
                <BarChart data={by_category} layout="vertical" margin={{left:20,right:20}}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e3a5f"/>
                  <XAxis type="number" tick={{fill:'#8899bb',fontSize:11}}/>
                  <YAxis type="category" dataKey="category" tick={{fill:'#8899bb',fontSize:11}} width={100}/>
                  <Tooltip {...TT}/><Bar dataKey="count" radius={[0,4,4,0]}>
                    {by_category.map((_,i)=><Cell key={i} fill={COLORS[i%COLORS.length]}/>)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
          }
        </div>
      </div>
      <div className="card">
        <div className="card-title">Interpretation Guide</div>
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16}}>
          {[
            {m:'Delivery Rate < 95%',  d:'Stale subscriptions — run GC',         c:'var(--danger)'},
            {m:'CTR < 5%',            d:'Content not actionable — improve copy', c:'var(--warn)'},
            {m:'Dismiss Rate > 40%',  d:'Notification fatigue — reduce frequency',c:'var(--warn)'},
            {m:'Sub Churn > 5%/week', d:'Poor relevance — personalize',          c:'var(--danger)'},
          ].map(x=>(
            <div key={x.m} style={{padding:'10px 14px',background:'var(--bg-primary)',borderRadius:8,borderLeft:`3px solid ${x.c}`}}>
              <div style={{fontSize:12,fontWeight:700,color:'var(--text-primary)',marginBottom:4}}>{x.m}</div>
              <div style={{fontSize:11,color:'var(--text-muted)'}}>{x.d}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const [page, setPage] = useState('overview');
  const [users, setUsers] = useState([]);
  const [analytics, setAnalytics] = useState(null);

  const loadAnalytics = useCallback(()=>{
    notificationsApi.getAnalytics().then(r=>setAnalytics(r.data)).catch(console.error);
  },[]);

  useEffect(()=>{
    usersApi.list().then(r=>setUsers(r.data)).catch(console.error);
    loadAnalytics();
    const iv = setInterval(loadAnalytics, 10000);
    return ()=>clearInterval(iv);
  },[loadAnalytics]);

  useEffect(()=>{
    usersApi.list().then(r=>{
      if(r.data.length===0) Promise.all([
        usersApi.create({username:'alice_devops',email:'alice@infrawatch.dev',role:'devops',timezone:'UTC'}),
        usersApi.create({username:'bob_sre',     email:'bob@infrawatch.dev',  role:'engineer',timezone:'UTC'}),
        usersApi.create({username:'carol_pm',    email:'carol@infrawatch.dev',role:'manager', timezone:'UTC'}),
      ]).then(()=>usersApi.list().then(r2=>setUsers(r2.data)));
    });
  },[]);

  return (
    <div className="layout">
      <Sidebar active={page} setActive={setPage}/>
      <div className="main-content">
        <div className="topbar">
          <div className="topbar-brand"><span>⚡</span> InfraWatch · Push Notifications</div>
          <div style={{display:'flex',gap:12,alignItems:'center'}}>
            <span className="badge badge-green">● Live</span>
            <span style={{color:'var(--text-muted)',fontSize:12}}>Day 130</span>
          </div>
        </div>
        {page==='overview'    && <OverviewPage analytics={analytics} users={users}/>}
        {page==='subscribe'   && <SubscribePage users={users} refresh={loadAnalytics}/>}
        {page==='preferences' && <PreferencesPage users={users} refresh={loadAnalytics}/>}
        {page==='send'        && <SendTestPage users={users} refresh={loadAnalytics}/>}
        {page==='analytics'   && <AnalyticsPage analytics={analytics}/>}
      </div>
    </div>
  );
}
DASHEOF

# ── DOCKER COMPOSE ────────────────────────────────────────────────────────────
cat > "$PROJECT_DIR/docker-compose.yml" << 'DCEOF'
version: '3.9'
services:
  backend:
    build: { context: ./backend, dockerfile: Dockerfile }
    container_name: infrawatch-push-backend
    ports: ["8130:8130"]
    environment: { DATABASE_URL: "sqlite+aiosqlite:///./infrawatch.db", ENVIRONMENT: development }
    volumes: ["./backend:/app"]
    restart: unless-stopped
    healthcheck:
      test: ["CMD","curl","-f","http://localhost:8130/health"]
      interval: 10s; timeout: 5s; retries: 5
  frontend:
    build: { context: ./frontend, dockerfile: Dockerfile }
    container_name: infrawatch-push-frontend
    ports: ["3130:80"]
    depends_on: [backend]
    restart: unless-stopped
DCEOF

cat > "$PROJECT_DIR/frontend/Dockerfile" << 'DKFEOF'
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
DKFEOF

cat > "$PROJECT_DIR/frontend/nginx.conf" << 'NGEOF'
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;
    location /api/ { proxy_pass http://backend:8130/api/; proxy_set_header Host $host; }
    location / { try_files $uri $uri/ /index.html; }
}
NGEOF

# ── VERIFY ALL FILES ──────────────────────────────────────────────────────────
info "Verifying file structure..."
REQUIRED=(
  backend/requirements.txt backend/.env backend/generate_vapid.py backend/main.py
  backend/app/config.py backend/app/database.py backend/app/models/models.py
  backend/app/schemas/schemas.py backend/app/services/push_service.py
  backend/app/services/scheduler_service.py backend/app/api/subscriptions.py
  backend/app/api/notifications.py backend/app/api/users.py backend/app/api/vapid.py
  backend/tests/conftest.py backend/tests/test_push_notifications.py
  frontend/package.json frontend/vite.config.js frontend/index.html
  frontend/public/sw.js frontend/public/manifest.json
  frontend/src/main.jsx frontend/src/App.jsx frontend/src/styles.css
  frontend/src/services/api.js frontend/src/hooks/usePushNotifications.js
  frontend/src/pages/Dashboard.jsx
)

ALL_OK=true
for f in "${REQUIRED[@]}"; do
  if [[ -f "$PROJECT_DIR/$f" ]]; then success "$f"
  else warn "MISSING: $f"; ALL_OK=false; fi
done
[[ "$ALL_OK" == "true" ]] || error "Required files missing — aborting"

# ── BUILD ─────────────────────────────────────────────────────────────────────
if [[ "$USE_DOCKER" == "true" ]]; then
  info "Building with Docker Compose..."
  cd "$PROJECT_DIR"
  docker compose build --no-cache && docker compose up -d
  for i in {1..30}; do
    curl -sf http://localhost:8130/health >/dev/null && success "Backend healthy" && break
    sleep 2
  done
else
  info "Building without Docker..."
  cd "$PROJECT_DIR/backend"
  # Ensure schema is recreated from current Day 130 models on each run.
  rm -f infrawatch.db
  python3 -m venv .venv
  source .venv/bin/activate
  pip install --quiet --upgrade pip
  pip install --quiet -r requirements.txt
  python generate_vapid.py
  cd "$PROJECT_DIR/frontend"
  npm install --silent
  success "Dependencies installed"
fi

# ── TESTS ─────────────────────────────────────────────────────────────────────
info "Running tests..."
cd "$PROJECT_DIR/backend"
[[ "$USE_DOCKER" == "false" ]] && source .venv/bin/activate
python -m pytest tests/ -v --tb=short 2>&1 | tee /tmp/test_output_130.txt
grep -qE "^FAILED|[0-9]+ failed" /tmp/test_output_130.txt && warn "Some tests failed" || success "All tests passed ✓"

# ── START SERVICES ────────────────────────────────────────────────────────────
if [[ "$USE_DOCKER" == "false" ]]; then
  info "Checking for existing Day 130 services..."
  pkill -f "uvicorn.*$BACKEND_PORT" 2>/dev/null || true
  pkill -f "vite.*$FRONTEND_PORT" 2>/dev/null || true
  sleep 1

  info "Starting backend on :$BACKEND_PORT..."
  cd "$PROJECT_DIR/backend"
  source .venv/bin/activate
  nohup uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT --reload > /tmp/infrawatch-backend-130.log 2>&1 &
  echo $! > /tmp/infrawatch-backend-130.pid
  info "Waiting for backend to be ready..."
  for i in {1..20}; do
    curl -sf http://localhost:$BACKEND_PORT/health >/dev/null 2>&1 && success "Backend running on :$BACKEND_PORT" && break
    sleep 1
    [[ $i -eq 20 ]] && warn "Backend slow to start -- check /tmp/infrawatch-backend-130.log"
  done

  info "Starting frontend on :$FRONTEND_PORT..."
  cd "$PROJECT_DIR/frontend"
  nohup npm run dev > /tmp/infrawatch-frontend-130.log 2>&1 &
  echo $! > /tmp/infrawatch-frontend-130.pid
  sleep 4
  success "Frontend running on :$FRONTEND_PORT"
fi

# ── DEMO ─────────────────────────────────────────────────────────────────────
info "Running functional demo..."
BASE="http://localhost:$BACKEND_PORT"
# backend already confirmed ready above

echo ""; echo "── Health ───────────────────────────────────────────────────────────────────"
curl -s $BASE/health | python3 -m json.tool

echo ""; echo "── Create users ─────────────────────────────────────────────────────────────"
U1=$(curl -s -X POST $BASE/api/users -H 'Content-Type: application/json' \
  -d '{"username":"demo_alice","email":"demo.alice@infrawatch.dev","role":"devops","timezone":"UTC"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "Alice (devops): $U1"
U2=$(curl -s -X POST $BASE/api/users -H 'Content-Type: application/json' \
  -d '{"username":"demo_bob","email":"demo.bob@infrawatch.dev","role":"manager","timezone":"UTC"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "Bob (manager):  $U2"

echo ""; echo "── Register subscriptions ───────────────────────────────────────────────────"
KEYS='{"p256dh":"BNcRdreALRFXTkOOUHK1EtK2wtBYALTNFY5K9vZdQZfVpL6mZ7TsRIb7A-aGNlrOJEWlYRnbP8Ep8k9bG9B3T1E=","auth":"tBHItJI5svbpez7KI4CCXg=="}'
curl -s -X POST $BASE/api/subscriptions -H 'Content-Type: application/json' \
  -d "{\"user_id\":\"$U1\",\"endpoint\":\"https://test.fcm.invalid/alice\",\"keys\":$KEYS}" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Alice sub: {d[\"id\"][:12]}... active={d[\"is_active\"]}')"
curl -s -X POST $BASE/api/subscriptions -H 'Content-Type: application/json' \
  -d "{\"user_id\":\"$U2\",\"endpoint\":\"https://test.fcm.invalid/bob\",\"keys\":$KEYS}" > /dev/null
echo "Bob subscribed"

echo ""; echo "── Alice prefs (devops defaults) ────────────────────────────────────────────"
curl -s $BASE/api/notifications/preferences/$U1 | python3 -m json.tool

echo ""; echo "── Bob prefs (manager defaults) ─────────────────────────────────────────────"
curl -s $BASE/api/notifications/preferences/$U2 | python3 -m json.tool

echo ""; echo "── Enable quiet hours for Alice (22:00–07:00) ───────────────────────────────"
curl -s -X PATCH $BASE/api/notifications/preferences/$U1 \
  -H 'Content-Type: application/json' \
  -d '{"quiet_hours_enabled":true,"quiet_hours_start":22,"quiet_hours_end":7}' | python3 -m json.tool

echo ""; echo "── Send notifications ────────────────────────────────────────────────────────"
N1=$(curl -s -X POST $BASE/api/notifications/send -H 'Content-Type: application/json' \
  -d "{\"user_id\":\"$U1\",\"category\":\"alerts\",\"title\":\"⚡ CPU Spike\",\"body\":\"prod-web-01 CPU 94%\",\"url\":\"/dashboard/alerts\"}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['notification_id'])")
echo "Alert ID: $N1"
N2=$(curl -s -X POST $BASE/api/notifications/send -H 'Content-Type: application/json' \
  -d "{\"user_id\":\"$U2\",\"category\":\"daily_digest\",\"title\":\"📋 Daily Digest\",\"body\":\"98% uptime today\",\"url\":\"/dashboard\"}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['notification_id'])")
echo "Digest ID: $N2"

echo ""; echo "── Record events ────────────────────────────────────────────────────────────"
curl -s -X POST $BASE/api/notifications/event -H 'Content-Type: application/json' \
  -d "{\"notification_id\":\"$N1\",\"event_type\":\"clicked\"}" | python3 -m json.tool
curl -s -X POST $BASE/api/notifications/event -H 'Content-Type: application/json' \
  -d "{\"notification_id\":\"$N2\",\"event_type\":\"dismissed\"}" | python3 -m json.tool

echo ""; echo "── Snooze Alice 60 min, then clear ──────────────────────────────────────────"
curl -s -X POST $BASE/api/notifications/snooze -H 'Content-Type: application/json' \
  -d "{\"user_id\":\"$U1\",\"duration_minutes\":60}" | python3 -m json.tool
curl -s -X DELETE $BASE/api/notifications/snooze/$U1 | python3 -m json.tool

echo ""; echo "── Analytics Summary ─────────────────────────────────────────────────────────"
curl -s $BASE/api/notifications/analytics | python3 -m json.tool

echo ""; echo "── VAPID Public Key ──────────────────────────────────────────────────────────"
curl -s $BASE/api/vapid/public-key | python3 -m json.tool

echo ""
success "══════════════════════════════════════════════════════"
success "Day 130 — Push Notifications complete!"
success "══════════════════════════════════════════════════════"
echo ""
echo -e "  ${CYAN}Backend API :${NC}  http://localhost:$BACKEND_PORT"
echo -e "  ${CYAN}Swagger Docs:${NC}  http://localhost:$BACKEND_PORT/docs"
echo -e "  ${CYAN}Frontend UI :${NC}  http://localhost:$FRONTEND_PORT"
echo ""
echo -e "  ${YELLOW}Stop:${NC}  ./setup.sh stop"
echo ""
info "Logs: /tmp/infrawatch-backend-130.log | /tmp/infrawatch-frontend-130.log"