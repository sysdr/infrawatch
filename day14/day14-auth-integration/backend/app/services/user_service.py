from typing import Optional, List, Dict
from app.models.user import UserCreate, UserResponse
from app.services.jwt_service import JWTService

# In-memory storage for demo (replace with database in production)
users_db: List[Dict] = []
user_id_counter = 1

class UserService:
    @staticmethod
    async def create_user(user_data: UserCreate) -> UserResponse:
        global user_id_counter
        hashed_password = JWTService.get_password_hash(user_data.password)
        
        user_dict = {
            "id": user_id_counter,
            "email": user_data.email,
            "username": user_data.username,
            "full_name": user_data.full_name,
            "hashed_password": hashed_password,
            "is_active": True,
            "created_at": "2025-01-01T00:00:00"
        }
        
        users_db.append(user_dict)
        user_id_counter += 1
        
        return UserResponse(**user_dict)

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[UserResponse]:
        for user in users_db:
            if user["email"] == email:
                return UserResponse(**user)
        return None

    @staticmethod
    async def get_user_by_id(user_id: int) -> Optional[UserResponse]:
        for user in users_db:
            if user["id"] == user_id:
                return UserResponse(**user)
        return None

    @staticmethod
    async def authenticate_user(email: str, password: str) -> Optional[UserResponse]:
        for user in users_db:
            if user["email"] == email:
                if JWTService.verify_password(password, user["hashed_password"]):
                    return UserResponse(**user)
        return None
