from fastapi import APIRouter, Query, Request
from typing import Optional
import hashlib, time

router = APIRouter()

USERS_V2 = [
    {"id":1,"first_name":"Alice","last_name":"Johnson","email":"alice@company.com","role":"admin","team_id":1,"status":"active","created_at":"2024-01-15T10:00:00Z","last_active":"2025-05-20T14:22:00Z"},
    {"id":2,"first_name":"Bob","last_name":"Smith","email":"bob@company.com","role":"engineer","team_id":1,"status":"active","created_at":"2024-02-01T09:00:00Z","last_active":"2025-05-21T11:10:00Z"},
    {"id":3,"first_name":"Carol","last_name":"White","email":"carol@company.com","role":"designer","team_id":2,"status":"active","created_at":"2024-03-15T08:30:00Z","last_active":"2025-05-19T16:45:00Z"},
    {"id":4,"first_name":"Dave","last_name":"Brown","email":"dave@company.com","role":"engineer","team_id":2,"status":"inactive","created_at":"2024-04-01T10:00:00Z","last_active":"2025-04-30T09:00:00Z"},
    {"id":5,"first_name":"Eve","last_name":"Davis","email":"eve@company.com","role":"manager","team_id":1,"status":"active","created_at":"2024-05-01T10:00:00Z","last_active":"2025-05-21T15:30:00Z"},
]
_next_id = 6

TEAMS_V2 = [
    {"id":1,"name":"Platform Engineering","member_total":3,"department":"Engineering","created_at":"2024-01-15","tags":["backend","infra"]},
    {"id":2,"name":"Product Design","member_total":2,"department":"Design","created_at":"2024-03-01","tags":["ui","ux"]},
]

WEBHOOKS = []

def _make_cursor(offset): return hashlib.md5(f"cursor_{offset}".encode()).hexdigest()[:12]

@router.get("/users")
async def list_users_v2(cursor: Optional[str]=None, per_page: int=Query(default=10,le=100), search: Optional[str]=None, role: Optional[str]=None, status: Optional[str]=None):
    data = list(USERS_V2)
    if search:
        data = [u for u in data if search.lower() in u["first_name"].lower() or search.lower() in u["last_name"].lower() or search.lower() in u["email"].lower()]
    if role:   data = [u for u in data if u["role"]==role]
    if status: data = [u for u in data if u["status"]==status]
    offset = 0
    if cursor:
        try: offset = int(cursor.split("_")[1]) if "_" in cursor else 0
        except: offset = 0
    page_data = data[offset:offset+per_page]
    has_more = (offset+per_page) < len(data)
    return {"data":page_data,"pagination":{"total":len(data),"per_page":per_page,"has_more":has_more,"next_cursor":_make_cursor(offset+per_page) if has_more else None},"meta":{"version":"v2"}}

@router.get("/users/{user_id}")
async def get_user_v2(user_id: int):
    user = next((u for u in USERS_V2 if u["id"]==user_id), None)
    if not user:
        return {"error":{"code":"USER_NOT_FOUND","message":f"User {user_id} does not exist","details":[],"request_id":f"req_{int(time.time())}"}}
    return {"data":user,"meta":{"version":"v2"}}

@router.post("/users")
async def create_user_v2(request: Request):
    global _next_id
    body = await request.json()
    errors = []
    if not body.get("first_name"): errors.append({"field":"first_name","message":"Required"})
    if not body.get("last_name"):  errors.append({"field":"last_name","message":"Required"})
    if not body.get("email"):      errors.append({"field":"email","message":"Required"})
    if errors:
        return {"error":{"code":"VALIDATION_ERROR","message":"Request validation failed","details":errors,"request_id":f"req_{int(time.time())}"}}
    new_user = {"id":_next_id,"first_name":body["first_name"],"last_name":body["last_name"],"email":body["email"],"role":body.get("role","engineer"),"team_id":body.get("team_id",1),"status":"active","created_at":"2025-05-21T00:00:00Z","last_active":"2025-05-21T00:00:00Z"}
    USERS_V2.append(new_user); _next_id += 1
    return {"data":new_user,"meta":{"version":"v2"}}

@router.get("/teams")
async def list_teams_v2():
    return {"data":TEAMS_V2,"pagination":{"total":len(TEAMS_V2)},"meta":{"version":"v2"}}

@router.get("/teams/{team_id}")
async def get_team_v2(team_id: int):
    team = next((t for t in TEAMS_V2 if t["id"]==team_id), None)
    if not team:
        return {"error":{"code":"TEAM_NOT_FOUND","message":f"Team {team_id} not found","details":[],"request_id":f"req_{int(time.time())}"}}
    members = [u for u in USERS_V2 if u["team_id"]==team_id]
    return {"data":{**team,"members":members},"meta":{"version":"v2"}}

@router.get("/analytics")
async def get_analytics_v2():
    return {"data":{"api_calls":{"total":125400,"v1":42300,"v2":83100},"errors":{"total":234,"rate":0.19},"latency_ms":{"p50":45,"p95":120,"p99":280},"uptime_pct":99.94,"active_clients":{"v1":18,"v2":47},"version_adoption":[{"version":"v1","calls_pct":33.7,"trend":"declining"},{"version":"v2","calls_pct":66.3,"trend":"growing"}]},"meta":{"version":"v2","window":"last_24h"}}

@router.get("/webhooks")
async def list_webhooks_v2():
    return {"data":WEBHOOKS,"meta":{"version":"v2"}}

@router.post("/webhooks")
async def create_webhook_v2(request: Request):
    body = await request.json()
    webhook = {"id":f"wh_{int(time.time())}","url":body.get("url"),"events":body.get("events",[]),"active":True,"created_at":"2025-05-21T00:00:00Z"}
    WEBHOOKS.append(webhook)
    return {"data":webhook,"meta":{"version":"v2"}}

@router.post("/auth/login")
async def login_v2(request: Request):
    return {"data":{"access_token":"v2_tok_xyz789","token_type":"Bearer","expires_in":3600,"refresh_token":"v2_refresh_abc456","user":{"id":1,"email":"alice@company.com","role":"admin"}},"meta":{"version":"v2"}}

@router.get("/compat/v1/users")
async def compat_v1_users():
    v1_shaped = [{"id":u["id"],"name":f"{u['first_name']} {u['last_name']}","email":u["email"],"role":u["role"],"team_id":u["team_id"]} for u in USERS_V2]
    return {"users":v1_shaped,"total":len(v1_shaped),"page":1,"limit":10,"pages":1}
