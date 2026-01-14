from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
from app.services.masking_service import masking_service

router = APIRouter()

class MaskTextRequest(BaseModel):
    text: str

class MaskDictRequest(BaseModel):
    data: Dict[str, Any]
    fields_to_mask: List[str] = None

class TokenizeRequest(BaseModel):
    value: str
    salt: str = "default"

@router.post("/mask-text")
async def mask_text(request: MaskTextRequest):
    """Automatically detect and mask PII in text"""
    try:
        masked = masking_service.mask_text(request.text)
        return {
            "success": True,
            "original_length": len(request.text),
            "masked_text": masked
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mask-dict")
async def mask_dict(request: MaskDictRequest):
    """Mask specified fields in a dictionary"""
    try:
        masked = masking_service.mask_dict(request.data, request.fields_to_mask)
        return {
            "success": True,
            "masked_data": masked
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mask-email")
async def mask_email(email: str):
    """Mask email address"""
    try:
        masked = masking_service.mask_email(email)
        return {
            "original": email,
            "masked": masked
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mask-phone")
async def mask_phone(phone: str):
    """Mask phone number"""
    try:
        masked = masking_service.mask_phone(phone)
        return {
            "original": phone,
            "masked": masked
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mask-ssn")
async def mask_ssn(ssn: str):
    """Mask SSN"""
    try:
        masked = masking_service.mask_ssn(ssn)
        return {
            "original": ssn,
            "masked": masked
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mask-credit-card")
async def mask_credit_card(credit_card: str):
    """Mask credit card number"""
    try:
        masked = masking_service.mask_credit_card(credit_card)
        return {
            "original": credit_card,
            "masked": masked
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tokenize")
async def tokenize(request: TokenizeRequest):
    """Tokenize value using one-way hash"""
    try:
        token = masking_service.tokenize(request.value, request.salt)
        return {
            "success": True,
            "token": token
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/patterns")
async def get_masking_patterns():
    """Get all PII detection patterns"""
    return {
        "patterns": list(masking_service.patterns.keys()),
        "total": len(masking_service.patterns)
    }
