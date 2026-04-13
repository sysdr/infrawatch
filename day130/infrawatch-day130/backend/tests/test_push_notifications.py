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
