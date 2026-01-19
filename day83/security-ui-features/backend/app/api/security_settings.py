from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from typing import List, Optional
import uuid

from app.core.database import get_db
from app.core.mock_data import get_mock_settings
from app.models.security_setting import SecuritySetting
from app.schemas.security_setting import SecuritySettingCreate, SecuritySettingUpdate, SecuritySettingResponse

router = APIRouter()

@router.get("/", response_model=List[SecuritySettingResponse])
async def get_security_settings(
    category: str = None,
    is_active: bool = None,
    db: Optional[Session] = Depends(get_db)
):
    """Get all security settings with optional filtering"""
    if db is None:
        mock_settings = get_mock_settings()
        if category:
            mock_settings = [s for s in mock_settings if s.get("category") == category]
        return mock_settings
    
    try:
        query = db.query(SecuritySetting)
        
        if category:
            query = query.filter(SecuritySetting.category == category)
        if is_active is not None:
            query = query.filter(SecuritySetting.is_active == is_active)
        
        settings = query.order_by(SecuritySetting.category, SecuritySetting.setting_name).all()
        return settings
    except (OperationalError, Exception) as e:
        print(f"Database error in get_security_settings: {e}")
        return get_mock_settings()

@router.get("/{setting_key}", response_model=SecuritySettingResponse)
async def get_security_setting(setting_key: str, db: Session = Depends(get_db)):
    """Get specific security setting"""
    setting = db.query(SecuritySetting).filter(SecuritySetting.setting_key == setting_key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Security setting not found")
    return setting

@router.post("/", response_model=SecuritySettingResponse)
async def create_security_setting(setting: SecuritySettingCreate, db: Session = Depends(get_db)):
    """Create new security setting"""
    # Check if setting already exists
    existing = db.query(SecuritySetting).filter(SecuritySetting.setting_key == setting.setting_key).first()
    if existing:
        raise HTTPException(status_code=400, detail="Security setting already exists")
    
    db_setting = SecuritySetting(**setting.model_dump())
    db.add(db_setting)
    db.commit()
    db.refresh(db_setting)
    return db_setting

@router.put("/{setting_key}", response_model=SecuritySettingResponse)
async def update_security_setting(
    setting_key: str,
    setting_update: SecuritySettingUpdate,
    db: Session = Depends(get_db)
):
    """Update security setting"""
    db_setting = db.query(SecuritySetting).filter(SecuritySetting.setting_key == setting_key).first()
    if not db_setting:
        raise HTTPException(status_code=404, detail="Security setting not found")
    
    update_data = setting_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_setting, field, value)
    
    db.commit()
    db.refresh(db_setting)
    return db_setting

@router.get("/categories/list")
async def get_setting_categories(db: Session = Depends(get_db)):
    """Get list of all setting categories"""
    categories = db.query(SecuritySetting.category).distinct().all()
    return {"categories": [cat[0] for cat in categories]}
