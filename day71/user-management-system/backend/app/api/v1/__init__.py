from fastapi import APIRouter
from .endpoints import (
    auth_router,
    users_router,
    profile_router,
    preferences_router,
    activity_router
)

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(profile_router)
api_router.include_router(preferences_router)
api_router.include_router(activity_router)
