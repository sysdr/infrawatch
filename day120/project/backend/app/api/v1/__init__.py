from fastapi import APIRouter, Query, Request
from typing import Optional

router = APIRouter()

USERS_V1 = [
    {"id":1,"name":"Alice Johnson","email":"alice@company.com","role":"admin","team_id":1},
    {"id":2,"name":"Bob Smith","email":"bob@company.com","role":"engineer","team_id":1},
    {"id":3,"name":"Carol White","email":"carol@company.com","role":"designer","team_id":2},
    {"id":4,"name":"Dave Brown","email":"dave@company.com","role":"engineer","team_id":2},
    {"id":5,"name":"Eve Davis","email":"eve@company.com","role":"manager","team_id":1},
]

TEAMS_V1 = [
    {"id":1,"name":"Platform Engineering","member_count":3,"created_at":"2024-01-15"},
    {"id":2,"name":"Product Design","member_count":2,"created_at":"2024-03-01"},
]

@router.get("/users")
async def list_users_v1(page: int = Query(default=1, ge=1), limit: int = Query(default=10, le=100), search: Optional[str] = None):
    data = USERS_V1
    if search:
        data = [u for u in data if search.lower() in u["name"].lower() or search.lower() in u["email"].lower()]
    offset = (page - 1) * limit
    return {"users": data[offset:offset+limit], "total": len(data), "page": page, "limit": limit, "pages": max(1,(len(data)+limit-1)//limit)}

@router.get("/users/{user_id}")
async def get_user_v1(user_id: int):
    user = next((u for u in USERS_V1 if u["id"] == user_id), None)
    return user if user else {"error": "User not found"}

@router.post("/users")
async def create_user_v1(request: Request):
    body = await request.json()
    new_user = {"id": max(u["id"] for u in USERS_V1)+1, "name": body.get("name",""), "email": body.get("email",""), "role": body.get("role","engineer"), "team_id": body.get("team_id",1)}
    USERS_V1.append(new_user)
    return new_user

@router.get("/teams")
async def list_teams_v1():
    return {"teams": TEAMS_V1, "total": len(TEAMS_V1)}

@router.get("/teams/{team_id}")
async def get_team_v1(team_id: int):
    team = next((t for t in TEAMS_V1 if t["id"] == team_id), None)
    return team if team else {"error": "Team not found"}

@router.get("/metrics")
async def get_metrics_v1():
    return {"api_calls":125400,"errors":234,"avg_response_ms":87,"uptime_pct":99.94}

@router.post("/auth/login")
async def login_v1(request: Request):
    return {"token":"v1_tok_abc123","user_id":1,"expires_in":3600}
