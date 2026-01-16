from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, Integer
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel
import uvicorn

from app.database import get_db, init_db
from app.redis_client import get_redis
from middleware.security_middleware import APISecurityMiddleware
from security.api_key_manager import APIKeyManager
from security.rate_limiter import RateLimiter
from security.ip_whitelist import IPWhitelist
from models.api_key import APIKey
from models.request_log import RequestLog

app = FastAPI(title="API Security System", version="1.0.0")

# CORS - Must be added first to handle all requests including errors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Security middleware (only for /api/* routes)
app.add_middleware(APISecurityMiddleware)

# ============= Pydantic Models =============

class APIKeyCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    permissions: Optional[List[str]] = []
    rate_limit: Optional[int] = 100
    rate_window: Optional[int] = 60
    ip_whitelist: Optional[List[str]] = []
    expires_in_days: Optional[int] = 90

class APIKeyResponse(BaseModel):
    id: str
    key_id: str
    name: str
    description: str
    prefix: str
    permissions: List[str]
    rate_limit: int
    rate_window: int
    ip_whitelist: List[str]
    is_active: bool
    is_revoked: bool
    created_at: datetime
    last_used_at: Optional[datetime]
    expires_at: Optional[datetime]

class APIKeyCreateResponse(BaseModel):
    api_key: APIKeyResponse
    full_key: str
    warning: str = "Store this key securely. It won't be shown again."

class RequestLogResponse(BaseModel):
    id: str
    api_key_id: str
    method: str
    path: str
    source_ip: str
    signature_valid: bool
    ip_whitelisted: bool
    rate_limited: bool
    status_code: int
    response_time_ms: int
    timestamp: datetime

class RateLimitStats(BaseModel):
    api_key_id: str
    total_requests: int
    rate_limited_requests: int
    avg_response_time: float
    period_start: datetime
    period_end: datetime

# ============= Startup Events =============

@app.on_event("startup")
async def startup_event():
    await init_db()
    print("Database initialized")

# ============= Health Check =============

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# ============= API Key Management =============

@app.post("/admin/api-keys", response_model=APIKeyCreateResponse)
async def create_api_key(
    key_data: APIKeyCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new API key"""
    
    # Validate IP whitelist CIDRs
    for cidr in key_data.ip_whitelist:
        if not IPWhitelist.validate_cidr(cidr):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid CIDR notation: {cidr}"
            )
    
    api_key_obj, full_key = await APIKeyManager.create_api_key(
        db=db,
        name=key_data.name,
        description=key_data.description,
        permissions=key_data.permissions,
        rate_limit=key_data.rate_limit,
        rate_window=key_data.rate_window,
        ip_whitelist=key_data.ip_whitelist,
        expires_in_days=key_data.expires_in_days
    )
    
    return APIKeyCreateResponse(
        api_key=APIKeyResponse(
            id=str(api_key_obj.id),
            key_id=api_key_obj.key_id,
            name=api_key_obj.name,
            description=api_key_obj.description,
            prefix=api_key_obj.prefix,
            permissions=api_key_obj.permissions,
            rate_limit=api_key_obj.rate_limit,
            rate_window=api_key_obj.rate_window,
            ip_whitelist=api_key_obj.ip_whitelist,
            is_active=api_key_obj.is_active,
            is_revoked=api_key_obj.is_revoked,
            created_at=api_key_obj.created_at,
            last_used_at=api_key_obj.last_used_at,
            expires_at=api_key_obj.expires_at
        ),
        full_key=full_key
    )

@app.get("/admin/api-keys", response_model=List[APIKeyResponse])
async def list_api_keys(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all API keys"""
    result = await db.execute(
        select(APIKey).offset(skip).limit(limit).order_by(APIKey.created_at.desc())
    )
    keys = result.scalars().all()
    
    return [
        APIKeyResponse(
            id=str(k.id),
            key_id=k.key_id,
            name=k.name,
            description=k.description,
            prefix=k.prefix,
            permissions=k.permissions,
            rate_limit=k.rate_limit,
            rate_window=k.rate_window,
            ip_whitelist=k.ip_whitelist,
            is_active=k.is_active,
            is_revoked=k.is_revoked,
            created_at=k.created_at,
            last_used_at=k.last_used_at,
            expires_at=k.expires_at
        )
        for k in keys
    ]

@app.delete("/admin/api-keys/{key_id}")
async def revoke_api_key(key_id: str, db: AsyncSession = Depends(get_db)):
    """Revoke an API key"""
    success = await APIKeyManager.revoke_api_key(db, key_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    return {"message": "API key revoked successfully"}

@app.post("/admin/api-keys/{key_id}/rotate")
async def rotate_api_key(key_id: str, db: AsyncSession = Depends(get_db)):
    """Rotate an API key"""
    new_key, full_key = await APIKeyManager.rotate_api_key(db, key_id)
    
    if not new_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    return {
        "new_key": APIKeyResponse(
            id=str(new_key.id),
            key_id=new_key.key_id,
            name=new_key.name,
            description=new_key.description,
            prefix=new_key.prefix,
            permissions=new_key.permissions,
            rate_limit=new_key.rate_limit,
            rate_window=new_key.rate_window,
            ip_whitelist=new_key.ip_whitelist,
            is_active=new_key.is_active,
            is_revoked=new_key.is_revoked,
            created_at=new_key.created_at,
            last_used_at=new_key.last_used_at,
            expires_at=new_key.expires_at
        ),
        "full_key": full_key,
        "warning": "Old key will be revoked in 24 hours. Update your applications."
    }

# ============= Request Logs =============

@app.get("/admin/request-logs", response_model=List[RequestLogResponse])
async def get_request_logs(
    skip: int = 0,
    limit: int = 100,
    api_key_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get request logs"""
    query = select(RequestLog)
    
    if api_key_id:
        query = query.where(RequestLog.api_key_id == api_key_id)
    
    query = query.offset(skip).limit(limit).order_by(RequestLog.timestamp.desc())
    
    result = await db.execute(query)
    logs = result.scalars().all()
    
    return [
        RequestLogResponse(
            id=str(log.id),
            api_key_id=log.api_key_id,
            method=log.method,
            path=log.path,
            source_ip=log.source_ip,
            signature_valid=log.signature_valid,
            ip_whitelisted=log.ip_whitelisted,
            rate_limited=log.rate_limited,
            status_code=log.status_code,
            response_time_ms=log.response_time_ms,
            timestamp=log.timestamp
        )
        for log in logs
    ]

# ============= Analytics =============

@app.get("/admin/analytics/rate-limits", response_model=List[RateLimitStats])
async def get_rate_limit_analytics(
    hours: int = 24,
    db: AsyncSession = Depends(get_db)
):
    """Get rate limiting analytics"""
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    result = await db.execute(
        select(
            RequestLog.api_key_id,
            func.count(RequestLog.id).label("total_requests"),
            func.sum(func.cast(RequestLog.rate_limited, Integer)).label("rate_limited_requests"),
            func.avg(RequestLog.response_time_ms).label("avg_response_time")
        )
        .where(RequestLog.timestamp >= start_time)
        .group_by(RequestLog.api_key_id)
    )
    
    stats = result.all()
    
    return [
        RateLimitStats(
            api_key_id=stat.api_key_id,
            total_requests=stat.total_requests,
            rate_limited_requests=stat.rate_limited_requests or 0,
            avg_response_time=float(stat.avg_response_time or 0),
            period_start=start_time,
            period_end=datetime.utcnow()
        )
        for stat in stats
    ]

# ============= Protected API Endpoints (Examples) =============

@app.get("/api/protected/data")
async def get_protected_data(request: Request):
    """Example protected endpoint"""
    api_key = request.state.api_key
    rate_info = request.state.rate_limit_info
    
    return {
        "message": "This is protected data",
        "api_key_name": api_key.name,
        "rate_limit": {
            "limit": rate_info["limit"],
            "remaining": rate_info["remaining"],
            "reset_at": rate_info["reset_at"]
        },
        "timestamp": datetime.utcnow()
    }

@app.post("/api/protected/action")
async def protected_action(request: Request, data: dict):
    """Example protected endpoint with request body"""
    api_key = request.state.api_key
    
    return {
        "message": "Action completed successfully",
        "api_key_name": api_key.name,
        "received_data": data,
        "timestamp": datetime.utcnow()
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
