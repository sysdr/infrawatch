from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from app.services.classification_service import classification_service, ClassificationLevel

router = APIRouter()

class ClassifyRequest(BaseModel):
    data: Dict[str, Any]

@router.post("/classify")
async def classify_data(request: ClassifyRequest):
    """Classify data fields"""
    try:
        classifications = classification_service.classify_data(request.data)
        
        result = {}
        for field, classification in classifications.items():
            result[field] = {
                "level": classification.name,
                "requires_encryption": classification_service.requires_encryption(classification),
                "retention_days": classification_service.get_retention_days(classification),
                "strategy": classification_service.get_encryption_strategy(classification)
            }
        
        return {
            "success": True,
            "classifications": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/field/{field_name}")
async def get_field_classification(field_name: str):
    """Get classification for a specific field"""
    classification = classification_service.classify_field(field_name)
    
    return {
        "field": field_name,
        "classification": classification.name,
        "level": classification.value,
        "requires_encryption": classification_service.requires_encryption(classification),
        "retention_days": classification_service.get_retention_days(classification)
    }

@router.get("/levels")
async def get_classification_levels():
    """Get all classification levels"""
    return {
        "levels": [
            {
                "name": level.name,
                "value": level.value,
                "requires_encryption": classification_service.requires_encryption(level),
                "retention_days": classification_service.get_retention_days(level),
                "strategy": classification_service.get_encryption_strategy(level)
            }
            for level in ClassificationLevel
        ]
    }

@router.get("/statistics")
async def get_classification_stats():
    """Get classification statistics"""
    # In production, query database for real stats
    return {
        "total_fields": len(classification_service.field_classifications),
        "by_level": {
            "public": 3,
            "internal": 3,
            "confidential": 3,
            "restricted": 5
        },
        "encrypted_fields": 8,
        "retention_policies": len(classification_service.retention_policies)
    }
