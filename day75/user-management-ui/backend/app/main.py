from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime, timedelta
from typing import List, Optional
import json
from pydantic import BaseModel
import asyncio

# Database setup
DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Association tables
user_teams = Table('user_teams', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('team_id', Integer, ForeignKey('teams.id'))
)

user_roles = Table('user_roles', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)

role_permissions = Table('role_permissions', Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id')),
    Column('permission_id', Integer, ForeignKey('permissions.id'))
)

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    avatar = Column(String, nullable=True)
    status = Column(String, default="active")
    last_active = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    teams = relationship("Team", secondary=user_teams, back_populates="members")
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    activities = relationship("Activity", back_populates="user")

class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    parent_id = Column(Integer, ForeignKey('teams.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    members = relationship("User", secondary=user_teams, back_populates="teams")
    children = relationship("Team", backref="parent", remote_side=[id])

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")

class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    resource = Column(String)
    action = Column(String)
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")

class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    action = Column(String)
    resource = Column(String)
    details = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="activities")

# Pydantic models
class UserBase(BaseModel):
    email: str
    name: str
    avatar: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = None
    avatar: Optional[str] = None
    status: Optional[str] = None

class UserResponse(UserBase):
    id: int
    status: str
    last_active: datetime
    created_at: datetime
    teams: List[str] = []
    roles: List[str] = []
    
    class Config:
        from_attributes = True

class TeamBase(BaseModel):
    name: str
    description: str
    parent_id: Optional[int] = None

class TeamCreate(TeamBase):
    pass

class TeamResponse(TeamBase):
    id: int
    created_at: datetime
    member_count: int = 0
    
    class Config:
        from_attributes = True

class RoleCreate(BaseModel):
    name: str
    description: str

class RoleResponse(BaseModel):
    id: int
    name: str
    description: str
    permission_count: int = 0
    
    class Config:
        from_attributes = True

class ActivityResponse(BaseModel):
    id: int
    user_id: int
    user_name: str
    action: str
    resource: str
    details: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(title="User Management API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize with sample data
def init_db():
    db = SessionLocal()
    
    # Check if already initialized
    if db.query(User).count() > 0:
        db.close()
        return
    
    # Create permissions
    permissions = [
        Permission(name="users.read", resource="users", action="read"),
        Permission(name="users.write", resource="users", action="write"),
        Permission(name="teams.read", resource="teams", action="read"),
        Permission(name="teams.write", resource="teams", action="write"),
        Permission(name="dashboards.read", resource="dashboards", action="read"),
        Permission(name="dashboards.write", resource="dashboards", action="write"),
    ]
    db.add_all(permissions)
    db.commit()
    
    # Create roles
    admin_role = Role(name="Admin", description="Full system access", permissions=permissions)
    editor_role = Role(name="Editor", description="Edit access", permissions=permissions[:4])
    viewer_role = Role(name="Viewer", description="Read-only access", permissions=[permissions[0], permissions[2], permissions[4]])
    
    db.add_all([admin_role, editor_role, viewer_role])
    db.commit()
    
    # Create teams
    engineering = Team(name="Engineering", description="Engineering team")
    frontend = Team(name="Frontend", description="Frontend developers", parent_id=None)
    backend = Team(name="Backend", description="Backend developers", parent_id=None)
    
    db.add_all([engineering, frontend, backend])
    db.commit()
    
    frontend.parent_id = engineering.id
    backend.parent_id = engineering.id
    db.commit()
    
    # Create users
    users = [
        User(email="alice@company.com", name="Alice Admin", status="active", 
             avatar="https://i.pravatar.cc/150?img=1", roles=[admin_role], teams=[engineering]),
        User(email="bob@company.com", name="Bob Builder", status="active",
             avatar="https://i.pravatar.cc/150?img=2", roles=[editor_role], teams=[frontend]),
        User(email="carol@company.com", name="Carol Coder", status="active",
             avatar="https://i.pravatar.cc/150?img=3", roles=[editor_role], teams=[backend]),
        User(email="dave@company.com", name="Dave Designer", status="inactive",
             avatar="https://i.pravatar.cc/150?img=4", roles=[viewer_role], teams=[frontend]),
    ]
    
    for i in range(5, 25):
        users.append(
            User(
                email=f"user{i}@company.com",
                name=f"User {i}",
                status="active" if i % 3 != 0 else "inactive",
                avatar=f"https://i.pravatar.cc/150?img={i}",
                roles=[viewer_role],
                teams=[frontend if i % 2 == 0 else backend]
            )
        )
    
    db.add_all(users)
    db.commit()
    
    # Create activities
    activities = [
        Activity(user_id=1, action="login", resource="system", details="Logged in from 192.168.1.1"),
        Activity(user_id=1, action="created", resource="dashboard", details="Created Q4 Metrics dashboard"),
        Activity(user_id=2, action="updated", resource="user", details="Updated profile information"),
        Activity(user_id=3, action="deleted", resource="alert", details="Deleted old alert rule"),
    ]
    db.add_all(activities)
    db.commit()
    
    db.close()

# API Endpoints
@app.on_event("startup")
async def startup():
    init_db()

@app.get("/")
async def root():
    return {"message": "User Management API", "version": "1.0.0"}

# User endpoints
@app.get("/api/users", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    status: Optional[str] = None,
    role: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(User)
    
    if search:
        query = query.filter(
            (User.name.contains(search)) | (User.email.contains(search))
        )
    if status:
        query = query.filter(User.status == status)
    if role:
        query = query.join(User.roles).filter(Role.name == role)
    
    users = query.offset(skip).limit(limit).all()
    
    return [
        UserResponse(
            **{**user.__dict__},
            teams=[t.name for t in user.teams],
            roles=[r.name for r in user.roles]
        )
        for user in users
    ]

@app.post("/api/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Broadcast activity
    await manager.broadcast({
        "type": "user_created",
        "user": {"id": db_user.id, "name": db_user.name, "email": db_user.email}
    })
    
    return UserResponse(**{**db_user.__dict__}, teams=[], roles=[])

@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        **{**user.__dict__},
        teams=[t.name for t in user.teams],
        roles=[r.name for r in user.roles]
    )

@app.put("/api/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    
    # Broadcast activity
    await manager.broadcast({
        "type": "user_updated",
        "user": {"id": user.id, "name": user.name, "email": user.email}
    })
    
    return UserResponse(**{**user.__dict__}, teams=[t.name for t in user.teams], roles=[r.name for r in user.roles])

@app.delete("/api/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    
    await manager.broadcast({
        "type": "user_deleted",
        "user": {"id": user_id}
    })
    
    return {"message": "User deleted"}

# Team endpoints
@app.get("/api/teams", response_model=List[TeamResponse])
async def get_teams(db: Session = Depends(get_db)):
    teams = db.query(Team).all()
    return [
        TeamResponse(**{**t.__dict__}, member_count=len(t.members))
        for t in teams
    ]

@app.post("/api/teams", response_model=TeamResponse)
async def create_team(team: TeamCreate, db: Session = Depends(get_db)):
    db_team = Team(**team.dict())
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    
    await manager.broadcast({
        "type": "team_created",
        "team": {"id": db_team.id, "name": db_team.name}
    })
    
    return TeamResponse(**{**db_team.__dict__}, member_count=0)

@app.post("/api/teams/{team_id}/members/{user_id}")
async def add_team_member(team_id: int, user_id: int, db: Session = Depends(get_db)):
    team = db.query(Team).filter(Team.id == team_id).first()
    user = db.query(User).filter(User.id == user_id).first()
    
    if not team or not user:
        raise HTTPException(status_code=404, detail="Team or user not found")
    
    if user not in team.members:
        team.members.append(user)
        db.commit()
    
    await manager.broadcast({
        "type": "team_member_added",
        "team": {"id": team_id, "name": team.name},
        "user": {"id": user_id, "name": user.name}
    })
    
    return {"message": "Member added"}

@app.delete("/api/teams/{team_id}/members/{user_id}")
async def remove_team_member(team_id: int, user_id: int, db: Session = Depends(get_db)):
    team = db.query(Team).filter(Team.id == team_id).first()
    user = db.query(User).filter(User.id == user_id).first()
    
    if not team or not user:
        raise HTTPException(status_code=404, detail="Team or user not found")
    
    if user in team.members:
        team.members.remove(user)
        db.commit()
    
    await manager.broadcast({
        "type": "team_member_removed",
        "team": {"id": team_id},
        "user": {"id": user_id}
    })
    
    return {"message": "Member removed"}

# Role endpoints
@app.get("/api/roles", response_model=List[RoleResponse])
async def get_roles(db: Session = Depends(get_db)):
    roles = db.query(Role).all()
    return [
        RoleResponse(**{**r.__dict__}, permission_count=len(r.permissions))
        for r in roles
    ]

@app.post("/api/users/{user_id}/roles/{role_id}")
async def assign_role(user_id: int, role_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    role = db.query(Role).filter(Role.id == role_id).first()
    
    if not user or not role:
        raise HTTPException(status_code=404, detail="User or role not found")
    
    if role not in user.roles:
        user.roles.append(role)
        db.commit()
    
    await manager.broadcast({
        "type": "role_assigned",
        "user": {"id": user_id, "name": user.name},
        "role": {"id": role_id, "name": role.name}
    })
    
    return {"message": "Role assigned"}

@app.delete("/api/users/{user_id}/roles/{role_id}")
async def revoke_role(user_id: int, role_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    role = db.query(Role).filter(Role.id == role_id).first()
    
    if not user or not role:
        raise HTTPException(status_code=404, detail="User or role not found")
    
    if role in user.roles:
        user.roles.remove(role)
        db.commit()
    
    await manager.broadcast({
        "type": "role_revoked",
        "user": {"id": user_id},
        "role": {"id": role_id}
    })
    
    return {"message": "Role revoked"}

# Activity endpoints
@app.get("/api/activities", response_model=List[ActivityResponse])
async def get_activities(
    skip: int = 0,
    limit: int = 50,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Activity).join(User)
    
    if user_id:
        query = query.filter(Activity.user_id == user_id)
    
    activities = query.order_by(Activity.timestamp.desc()).offset(skip).limit(limit).all()
    
    return [
        ActivityResponse(
            **{**a.__dict__},
            user_name=a.user.name
        )
        for a in activities
    ]

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo for heartbeat
            await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
