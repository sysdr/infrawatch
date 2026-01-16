from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.redis_client import get_redis
from security.api_key_manager import APIKeyManager
from security.rate_limiter import RateLimiter
from security.request_signer import RequestSigner
from security.ip_whitelist import IPWhitelist
from models.request_log import RequestLog
import time

class APISecurityMiddleware(BaseHTTPMiddleware):
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Skip security for health check, public endpoints, and admin endpoints
        if request.url.path in ["/health", "/", "/docs", "/openapi.json"] or request.url.path.startswith("/admin"):
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host
        if "x-forwarded-for" in request.headers:
            client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()
        
        # Extract API key from header
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Missing API key"},
                headers={"WWW-Authenticate": "API-Key"}
            )
        
        # Validate API key
        async with AsyncSessionLocal() as db:
            key_obj = await APIKeyManager.validate_api_key(db, api_key)
            
            if not key_obj:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"error": "Invalid or expired API key"}
                )
            
            # Check IP whitelist
            if key_obj.ip_whitelist:
                if not IPWhitelist.is_ip_whitelisted(client_ip, key_obj.ip_whitelist):
                    await self._log_request(
                        db, key_obj.key_id, request, client_ip,
                        status.HTTP_403_FORBIDDEN, False, False, False
                    )
                    return JSONResponse(
                        status_code=status.HTTP_403_FORBIDDEN,
                        content={"error": "IP address not whitelisted"}
                    )
            
            # Check rate limit
            redis = await get_redis()
            allowed, rate_info = await RateLimiter.check_rate_limit(
                redis, key_obj.key_id, key_obj.rate_limit, key_obj.rate_window
            )
            
            if not allowed:
                await self._log_request(
                    db, key_obj.key_id, request, client_ip,
                    status.HTTP_429_TOO_MANY_REQUESTS, False, True, True
                )
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "Rate limit exceeded",
                        "retry_after": rate_info.get("retry_after", 60)
                    },
                    headers={
                        "X-RateLimit-Limit": str(rate_info["limit"]),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(rate_info["reset_at"]),
                        "Retry-After": str(rate_info.get("retry_after", 60))
                    }
                )
            
            # Verify request signature (if provided)
            signature_valid = True
            signature = request.headers.get("X-Signature")
            timestamp = request.headers.get("X-Timestamp")
            
            if signature and timestamp:
                body = ""
                if request.method in ["POST", "PUT", "PATCH"]:
                    body_bytes = await request.body()
                    body = body_bytes.decode()
                
                # Extract secret from API key (split on first 2 underscores only)
                secret = api_key.split("_", 2)[-1]
                
                signature_valid, error = RequestSigner.verify_signature(
                    secret, timestamp, request.method, 
                    str(request.url.path), body, signature
                )
            
            # Store request context for handler
            request.state.api_key = key_obj
            request.state.rate_limit_info = rate_info
            
            # Process request
            response = await call_next(request)
            
            # Add security headers
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["Content-Security-Policy"] = "default-src 'self'"
            response.headers["X-API-Version"] = "v1.2025.05"
            
            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(rate_info["limit"])
            response.headers["X-RateLimit-Remaining"] = str(rate_info["remaining"])
            response.headers["X-RateLimit-Reset"] = str(rate_info["reset_at"])
            
            # Log request
            response_time = int((time.time() - start_time) * 1000)
            await self._log_request(
                db, key_obj.key_id, request, client_ip,
                response.status_code, signature_valid, True, False, response_time
            )
            
            return response
    
    async def _log_request(
        self, db: AsyncSession, api_key_id: str, request: Request,
        client_ip: str, status_code: int, signature_valid: bool,
        ip_whitelisted: bool, rate_limited: bool, response_time: int = 0
    ):
        """Log API request"""
        log = RequestLog(
            api_key_id=api_key_id,
            method=request.method,
            path=str(request.url.path),
            source_ip=client_ip,
            user_agent=request.headers.get("user-agent", ""),
            signature_valid=signature_valid,
            ip_whitelisted=ip_whitelisted,
            rate_limited=rate_limited,
            status_code=status_code,
            response_time_ms=response_time,
            headers=dict(request.headers)
        )
        db.add(log)
        await db.commit()
