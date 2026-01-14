from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List
import secrets
import json

from app.core.database import get_db
from app.core.redis_client import get_redis
from app.models.auth import User, MFAConfig, Device, OAuthClient, OAuthCode, RiskEvent
from app.auth.mfa import MFAService
from app.auth.oauth2 import OAuth2Service
from app.auth.device import DeviceService
from app.auth.risk import RiskAssessmentService
from app.auth.sessions import SessionService
from passlib.hash import argon2

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Initialize services
mfa_service = MFAService()
from app.core.config import settings
oauth2_service = OAuth2Service(settings.SECRET_KEY)

@router.post("/register")
async def register(
    email: str,
    username: str,
    password: str,
    db: Session = Depends(get_db)
):
    """Register new user"""
    # Check if user exists
    existing = db.query(User).filter(
        (User.email == email) | (User.username == username)
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create user
    user = User(
        email=email,
        username=username,
        password_hash=argon2.hash(password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {"user_id": str(user.id), "message": "User registered successfully"}

@router.post("/login")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    redis = Depends(get_redis)
):
    """Login with risk assessment"""
    # Find user
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not argon2.verify(form_data.password, user.password_hash):
        # Record failed attempt
        if user:
            risk_service = RiskAssessmentService(redis)
            risk_service.record_failed_attempt(str(user.id))
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Get request metadata
    ip_address = request.client.host
    user_agent = request.headers.get("user-agent", "")
    
    # Assess risk
    risk_service = RiskAssessmentService(redis)
    risk_score, action = await risk_service.assess_login_risk(
        user_id=str(user.id),
        ip=ip_address,
        device_id="",  # Will be generated from fingerprint
        location={"country": "US", "lat": 0, "lon": 0}
    )
    
    # Log risk event
    risk_event = RiskEvent(
        user_id=user.id,
        risk_score=risk_score,
        factors={"ip": ip_address, "user_agent": user_agent},
        action_taken=action,
        ip_address=ip_address
    )
    db.add(risk_event)
    db.commit()
    
    # Check if MFA is required
    mfa_config = db.query(MFAConfig).filter(MFAConfig.user_id == user.id).first()
    requires_mfa = mfa_config and mfa_config.totp_secret and (action in ["require_mfa", "require_email_verification"])
    
    if action == "block":
        raise HTTPException(status_code=403, detail="Login blocked due to high risk")
    
    # Clear failed attempts
    risk_service.clear_failed_attempts(str(user.id))
    
    # Create session
    session_service = SessionService(redis)
    session_id = session_service.create_session(
        user_id=str(user.id),
        device_id="temp_device",
        ip=ip_address,
        user_agent=user_agent,
        mfa_verified=not requires_mfa
    )
    
    # Generate tokens
    access_token = oauth2_service.create_access_token(
        user_id=str(user.id),
        scopes=["read", "write"],
        expires_delta=timedelta(minutes=15)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "requires_mfa": requires_mfa,
        "session_id": session_id,
        "risk_score": risk_score
    }

@router.post("/mfa/setup")
async def setup_mfa(
    user_id: str = Query(..., description="User ID for MFA setup"),
    db: Session = Depends(get_db)
):
    """Setup MFA for user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate TOTP secret
    secret = mfa_service.generate_totp_secret()
    qr_code = mfa_service.generate_qr_code(secret, user.email)
    backup_codes = mfa_service.generate_backup_codes()
    
    # Store MFA config
    mfa_config = db.query(MFAConfig).filter(MFAConfig.user_id == user.id).first()
    if not mfa_config:
        mfa_config = MFAConfig(user_id=user.id)
        db.add(mfa_config)
    
    mfa_config.totp_secret = secret
    mfa_config.backup_codes = backup_codes
    mfa_config.enabled_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "secret": secret,
        "qr_code": qr_code,
        "backup_codes": [code["code"] for code in backup_codes]
    }

@router.post("/mfa/verify")
async def verify_mfa(
    user_id: str = Query(..., description="User ID"),
    token: str = Query(..., description="MFA verification token"),
    db: Session = Depends(get_db),
    redis = Depends(get_redis)
):
    """Verify MFA token"""
    mfa_config = db.query(MFAConfig).filter(MFAConfig.user_id == user_id).first()
    if not mfa_config or not mfa_config.totp_secret:
        raise HTTPException(status_code=400, detail="MFA not configured")
    
    # Verify TOTP with a wider time window to account for network delays
    # valid_window=2 means we accept codes from ±2 time steps (60 seconds total window)
    is_valid = mfa_service.verify_totp(mfa_config.totp_secret, token, valid_window=2)
    
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid MFA token. The code may have expired. Please generate a new code.")
    
    # Update session
    session_service = SessionService(redis)
    sessions = session_service.get_user_sessions(user_id)
    if sessions:
        latest_session = sessions[0]
        latest_session["mfa_verified"] = True
        redis.setex(
            f"session:{user_id}:{latest_session['session_id']}",
            86400,
            json.dumps(latest_session)
        )
    
    return {"message": "MFA verified successfully"}

@router.post("/mfa/generate-code")
async def generate_totp_code(
    secret: str = Query(..., description="TOTP secret to generate code from")
):
    """Generate current TOTP code from secret (for testing/demo purposes)"""
    try:
        import pyotp
        totp = pyotp.TOTP(secret)
        current_code = totp.now()
        return {"code": current_code}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to generate code: {str(e)}")

@router.get("/sessions")
async def get_sessions(
    user_id: str = Query(..., description="User ID"),
    redis = Depends(get_redis)
):
    """Get all active sessions"""
    session_service = SessionService(redis)
    sessions = session_service.get_user_sessions(user_id)
    return {"sessions": sessions}

@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    user_id: str = Query(..., description="User ID"),
    redis = Depends(get_redis)
):
    """Revoke specific session"""
    session_service = SessionService(redis)
    session_service.revoke_session(user_id, session_id)
    return {"message": "Session revoked"}

@router.post("/device/fingerprint")
async def register_device(
    fingerprint_data: dict,
    user_id: str = Query(..., description="User ID"),
    request: Request = None,
    db: Session = Depends(get_db),
    redis = Depends(get_redis)
):
    """Register device fingerprint"""
    if request is None:
        from fastapi import Request as FastAPIRequest
        # This shouldn't happen, but handle it gracefully
        pass
    """Register device fingerprint"""
    device_id = DeviceService.generate_fingerprint(fingerprint_data)
    
    # Check if device exists
    device = db.query(Device).filter(Device.device_id == device_id).first()
    
    if not device:
        device = Device(
            device_id=device_id,
            user_id=user_id,
            fingerprint=fingerprint_data,
            ip_addresses=[request.client.host],
            user_agent=request.headers.get("user-agent", "")
        )
        db.add(device)
    else:
        device.last_seen = datetime.utcnow()
        device.login_count += 1
        if request.client.host not in device.ip_addresses:
            device.ip_addresses.append(request.client.host)
    
    db.commit()
    
    return {"device_id": device_id, "trust_score": device.trust_score}

@router.get("/risk/history")
async def get_risk_history(
    user_id: str = Query(..., description="User ID"),
    limit: int = Query(50, description="Number of events to return"),
    db: Session = Depends(get_db)
):
    """Get risk assessment history"""
    events = db.query(RiskEvent).filter(
        RiskEvent.user_id == user_id
    ).order_by(RiskEvent.created_at.desc()).limit(limit).all()
    
    return {
        "events": [
            {
                "risk_score": e.risk_score,
                "action": e.action_taken,
                "ip": e.ip_address,
                "timestamp": e.created_at.isoformat()
            }
            for e in events
        ]
    }

# OAuth2 routes
@router.get("/oauth/authorize")
async def oauth_authorize(
    client_id: str,
    redirect_uri: str,
    code_challenge: str,
    code_challenge_method: str = "S256",
    scope: str = "read",
    db: Session = Depends(get_db)
):
    """OAuth2 authorization endpoint"""
    # Verify client
    client = db.query(OAuthClient).filter(OAuthClient.client_id == client_id).first()
    if not client:
        raise HTTPException(status_code=400, detail="Invalid client")
    
    # In production, show consent screen here
    # For demo, auto-approve
    
    # Generate authorization code
    auth_code = oauth2_service.generate_authorization_code()
    
    # Store code
    code_entry = OAuthCode(
        code=auth_code,
        client_id=client_id,
        user_id="demo-user-id",  # From authenticated session
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
        redirect_uri=redirect_uri,
        scope=scope,
        expires_at=datetime.utcnow() + timedelta(minutes=10)
    )
    db.add(code_entry)
    db.commit()
    
    return {"authorization_code": auth_code, "redirect_uri": redirect_uri}

@router.post("/oauth/token")
async def oauth_token(
    code: str,
    code_verifier: str,
    client_id: str,
    db: Session = Depends(get_db)
):
    """OAuth2 token endpoint"""
    # Verify code
    code_entry = db.query(OAuthCode).filter(OAuthCode.code == code).first()
    if not code_entry or code_entry.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired code")
    
    # Verify PKCE challenge
    if not oauth2_service.verify_code_challenge(code_verifier, code_entry.code_challenge):
        raise HTTPException(status_code=400, detail="Invalid code verifier")
    
    # Generate tokens
    access_token = oauth2_service.create_access_token(
        user_id=str(code_entry.user_id),
        scopes=code_entry.scope.split(),
        expires_delta=timedelta(minutes=15)
    )
    refresh_token = oauth2_service.create_refresh_token(str(code_entry.user_id))
    
    # Delete used code
    db.delete(code_entry)
    db.commit()
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 900,
        "refresh_token": refresh_token
    }
