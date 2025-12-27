from .auth import router as auth_router
from .users import router as users_router
from .profile import router as profile_router
from .preferences import router as preferences_router
from .activity import router as activity_router

__all__ = [
    "auth_router",
    "users_router",
    "profile_router",
    "preferences_router",
    "activity_router"
]
