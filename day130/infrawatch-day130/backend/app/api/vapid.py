from fastapi import APIRouter
from app.config import get_settings

router = APIRouter(prefix="/api/vapid", tags=["vapid"])

@router.get("/public-key")
async def get_vapid_public_key():
    return {"public_key": get_settings().VAPID_PUBLIC_KEY}
