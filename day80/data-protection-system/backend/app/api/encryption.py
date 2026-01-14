from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.services.encryption_service import encryption_service
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class EncryptRequest(BaseModel):
    plaintext: str
    context: str = "default"

class DecryptRequest(BaseModel):
    encrypted_data: dict

@router.post("/encrypt")
async def encrypt_data(request: EncryptRequest):
    """Encrypt data using AES-256-GCM"""
    try:
        encrypted = encryption_service.encrypt(request.plaintext, request.context)
        return {
            "success": True,
            "encrypted_data": encrypted,
            "algorithm": "AES-256-GCM"
        }
    except Exception as e:
        logger.error(f"Encryption error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/decrypt")
async def decrypt_data(request: DecryptRequest):
    """Decrypt previously encrypted data"""
    try:
        plaintext = encryption_service.decrypt(request.encrypted_data)
        return {
            "success": True,
            "plaintext": plaintext
        }
    except Exception as e:
        logger.error(f"Decryption error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rotate-keys")
async def rotate_keys():
    """Rotate encryption keys"""
    try:
        result = encryption_service.rotate_keys()
        return {
            "success": True,
            "rotation": result
        }
    except Exception as e:
        logger.error(f"Key rotation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/key-status")
async def key_status():
    """Get encryption key status"""
    return {
        "current_version": encryption_service.key_version,
        "cached_deks": len(encryption_service.dek_cache),
        "status": "active"
    }

@router.post("/encrypt-user")
async def encrypt_user_data(user_id: int, db: Session = Depends(get_db)):
    """Encrypt all sensitive fields for a user"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Encrypt sensitive fields
        if user.email:
            user.email_encrypted = str(encryption_service.encrypt(user.email, f"user:{user_id}:email")).encode()
        if user.full_name:
            user.full_name_encrypted = str(encryption_service.encrypt(user.full_name, f"user:{user_id}:name")).encode()
        if user.phone:
            user.phone_encrypted = str(encryption_service.encrypt(user.phone, f"user:{user_id}:phone")).encode()
        
        db.commit()
        
        return {
            "success": True,
            "user_id": user_id,
            "encrypted_fields": ["email", "full_name", "phone"]
        }
    except Exception as e:
        logger.error(f"User encryption error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
