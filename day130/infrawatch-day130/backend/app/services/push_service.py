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
