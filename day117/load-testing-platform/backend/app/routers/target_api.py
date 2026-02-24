"""
Self-contained target API that simulates User & Team Management endpoints.
This is the System Under Test (SUT) for our load tests.
"""
import asyncio, random, time
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List, Optional
from faker import Faker

router = APIRouter(prefix="/api", tags=["target"])
fake = Faker()

# Simulate an in-memory dataset (to avoid DB bottleneck being the focus)
_users = [{"id": i, "name": fake.name(), "email": fake.email(), "role": random.choice(["admin","member","viewer"])} for i in range(1, 501)]
_teams = [{"id": i, "name": f"Team-{fake.word().capitalize()}", "members": random.randint(3,20)} for i in range(1, 51)]

class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None

@router.get("/health")
async def health():
    return {"status": "ok", "timestamp": time.time()}

@router.get("/users")
async def list_users(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100)):
    # Simulate variable latency (20-80ms)
    await asyncio.sleep(random.uniform(0.02, 0.08))
    start = (page - 1) * limit
    return {"users": _users[start:start+limit], "total": len(_users), "page": page}

@router.get("/users/{user_id}")
async def get_user(user_id: int):
    await asyncio.sleep(random.uniform(0.01, 0.05))
    user = next((u for u in _users if u["id"] == user_id), None)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/users/{user_id}")
async def update_user(user_id: int, update: UserUpdate):
    await asyncio.sleep(random.uniform(0.03, 0.12))
    for u in _users:
        if u["id"] == user_id:
            if update.name: u["name"] = update.name
            if update.role: u["role"] = update.role
            return u
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="User not found")

@router.get("/teams")
async def list_teams():
    await asyncio.sleep(random.uniform(0.015, 0.06))
    return {"teams": _teams, "total": len(_teams)}

@router.get("/teams/{team_id}")
async def get_team(team_id: int):
    await asyncio.sleep(random.uniform(0.01, 0.04))
    team = next((t for t in _teams if t["id"] == team_id), None)
    if not team:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Team not found")
    return team

@router.get("/teams/{team_id}/members")
async def get_team_members(team_id: int):
    await asyncio.sleep(random.uniform(0.02, 0.09))
    return {"team_id": team_id, "members": random.sample(_users, min(10, len(_users)))}

@router.post("/auth/login")
async def login(payload: dict):
    await asyncio.sleep(random.uniform(0.05, 0.15))
    return {"token": fake.sha256(), "expires_in": 3600}

@router.get("/dashboard/stats")
async def dashboard_stats():
    await asyncio.sleep(random.uniform(0.04, 0.1))
    return {
        "total_users": len(_users),
        "total_teams": len(_teams),
        "active_sessions": random.randint(50, 200),
        "requests_today": random.randint(1000, 50000)
    }
