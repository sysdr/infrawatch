from sqlalchemy.orm import Session
from models.user import User

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_data: dict):
        user = User(**user_data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user(self, user_id: int):
        return self.db.query(User).filter(User.id == user_id).first()
    
    def list_users(self, skip: int = 0, limit: int = 100):
        return self.db.query(User).offset(skip).limit(limit).all()
