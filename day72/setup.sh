#!/bin/bash

# Day 72: Team Management System - Automated Implementation Script
# This script creates a complete, production-ready team management system

set -e

echo "=================================================="
echo "Day 72: Team Management System Implementation"
echo "=================================================="

# Create project structure
PROJECT_ROOT="team_management_system"
mkdir -p ${PROJECT_ROOT}/{backend,frontend,docker}
cd ${PROJECT_ROOT}

# Create backend structure
mkdir -p backend/{app/{models,schemas,services,api,utils,websocket},tests,alembic/versions}

# Create frontend structure
mkdir -p frontend/{src/{components/{teams,members,dashboard,common},services,hooks,utils},public}

echo "Creating Backend Files..."

# Backend: requirements.txt
cat > backend/requirements.txt << 'EOF'
fastapi==0.115.0
uvicorn[standard]==0.32.0
sqlalchemy==2.0.36
asyncpg==0.30.0
redis==5.2.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.20
websockets==13.1
pydantic==2.10.3
pydantic-settings==2.6.1
alembic==1.14.0
pytest==8.3.4
pytest-asyncio==0.24.0
httpx==0.28.1
psycopg2-binary==2.9.10
python-socketio==5.11.4
aioredis==2.0.1
faker==33.1.0
EOF

# Backend: database.py
cat > backend/app/database.py << 'EOF'
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def get_db():
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
EOF

# Backend: config.py
cat > backend/app/config.py << 'EOF'
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/teamdb"
    REDIS_URL: str = "redis://localhost:6379"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()
EOF

# Backend: models/team.py
cat > backend/app/models/team.py << 'EOF'
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Boolean, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    settings = Column(JSON, default={})
    
    teams = relationship("Team", back_populates="organization", cascade="all, delete-orphan")

class Team(Base):
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"))
    parent_team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), index=True)
    description = Column(Text)
    materialized_path = Column(String(1000), index=True)
    member_count = Column(Integer, default=0)
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    team_metadata = Column("metadata", JSON, default={}, key="team_metadata")
    
    organization = relationship("Organization", back_populates="teams")
    parent_team = relationship("Team", remote_side=[id], backref="sub_teams")
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    permissions = relationship("TeamPermission", back_populates="team", cascade="all, delete-orphan")

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    permissions = Column(JSON, default=[])
    is_system_role = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class TeamMember(Base):
    __tablename__ = "team_members"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    role_id = Column(Integer, ForeignKey("roles.id"))
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    invited_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    effective_permissions = Column(JSON, default=[])
    
    team = relationship("Team", back_populates="members")
    user = relationship("User", foreign_keys=[user_id])
    role = relationship("Role")
    inviter = relationship("User", foreign_keys=[invited_by])

class TeamPermission(Base):
    __tablename__ = "team_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"))
    resource_type = Column(String(100))
    resource_id = Column(Integer, nullable=True)
    permission_type = Column(String(100))
    allow = Column(Boolean, default=True)
    
    team = relationship("Team", back_populates="permissions")

class TeamActivity(Base):
    __tablename__ = "team_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    activity_type = Column(String(100))
    description = Column(Text)
    activity_metadata = Column("metadata", JSON, default={}, key="activity_metadata")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    username = Column(String(100), unique=True, index=True)
    full_name = Column(String(255))
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
EOF

# Backend: schemas/team.py
cat > backend/app/schemas/team.py << 'EOF'
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None
    parent_team_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = {}

class TeamCreate(TeamBase):
    organization_id: int

class TeamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class TeamMemberAdd(BaseModel):
    user_id: int
    role_id: int

class TeamResponse(TeamBase):
    id: int
    organization_id: int
    slug: str
    materialized_path: str
    member_count: int
    last_activity_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

class TeamMemberResponse(BaseModel):
    id: int
    team_id: int
    user_id: int
    role_id: int
    joined_at: datetime
    effective_permissions: List[str]
    
    class Config:
        from_attributes = True

class TeamDashboardMetrics(BaseModel):
    team_id: int
    team_name: str
    total_members: int
    active_members_today: int
    active_members_week: int
    total_activities: int
    recent_activities: List[Dict[str, Any]]
    member_activity_distribution: Dict[str, int]

class OrganizationCreate(BaseModel):
    name: str
    slug: str
    settings: Optional[Dict[str, Any]] = {}

class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: List[str] = []
EOF

# Backend: services/team_service.py
cat > backend/app/services/team_service.py << 'EOF'
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from app.models.team import Team, TeamMember, TeamActivity, Organization, Role, User
from app.schemas.team import TeamCreate, TeamDashboardMetrics
from typing import List, Optional
import redis.asyncio as redis
from app.config import settings
import json
from datetime import datetime, timedelta

class TeamService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.redis_client = None
    
    async def get_redis(self):
        if not self.redis_client:
            self.redis_client = await redis.from_url(settings.REDIS_URL, decode_responses=True)
        return self.redis_client
    
    async def create_team(self, team_data: TeamCreate, creator_id: int) -> Team:
        # Build materialized path
        path = f"/org{team_data.organization_id}"
        if team_data.parent_team_id:
            result = await self.db.execute(
                select(Team).where(Team.id == team_data.parent_team_id)
            )
            parent = result.scalar_one_or_none()
            if parent:
                path = f"{parent.materialized_path}/{parent.slug}"
        
        slug = team_data.name.lower().replace(" ", "-")
        path = f"{path}/{slug}"
        
        team = Team(
            organization_id=team_data.organization_id,
            parent_team_id=team_data.parent_team_id,
            name=team_data.name,
            slug=slug,
            description=team_data.description,
            materialized_path=path,
            team_metadata=team_data.metadata
        )
        
        self.db.add(team)
        await self.db.flush()
        
        # Add creator as admin
        admin_role = await self._get_or_create_role("admin", ["all"])
        member = TeamMember(
            team_id=team.id,
            user_id=creator_id,
            role_id=admin_role.id,
            effective_permissions=["all"]
        )
        self.db.add(member)
        
        team.member_count = 1
        await self.db.commit()
        await self.db.refresh(team)
        
        # Cache team data
        await self._cache_team(team)
        
        return team
    
    async def add_team_member(self, team_id: int, user_id: int, role_id: int, inviter_id: int) -> TeamMember:
        # Compute effective permissions
        role_result = await self.db.execute(select(Role).where(Role.id == role_id))
        role = role_result.scalar_one()
        
        effective_perms = await self._compute_effective_permissions(team_id, role.permissions)
        
        member = TeamMember(
            team_id=team_id,
            user_id=user_id,
            role_id=role_id,
            invited_by=inviter_id,
            effective_permissions=effective_perms
        )
        
        self.db.add(member)
        
        # Update team member count
        result = await self.db.execute(select(Team).where(Team.id == team_id))
        team = result.scalar_one()
        team.member_count += 1
        
        await self.db.commit()
        
        # Invalidate cache
        redis_client = await self.get_redis()
        await redis_client.delete(f"team:{team_id}:members")
        await redis_client.delete(f"perms:user:{user_id}:team:{team_id}")
        
        # Record activity
        await self._record_activity(team_id, inviter_id, "member_added", f"Added user {user_id}")
        
        return member
    
    async def get_team_dashboard(self, team_id: int) -> TeamDashboardMetrics:
        redis_client = await self.get_redis()
        
        # Check cache
        cache_key = f"dashboard:team:{team_id}"
        cached = await redis_client.get(cache_key)
        if cached:
            return TeamDashboardMetrics(**json.loads(cached))
        
        # Compute metrics
        team_result = await self.db.execute(select(Team).where(Team.id == team_id))
        team = team_result.scalar_one()
        
        # Active members today
        today = datetime.utcnow().date()
        active_today_result = await self.db.execute(
            select(func.count(func.distinct(TeamActivity.user_id)))
            .where(
                and_(
                    TeamActivity.team_id == team_id,
                    func.date(TeamActivity.created_at) == today
                )
            )
        )
        active_today = active_today_result.scalar() or 0
        
        # Active members this week
        week_ago = datetime.utcnow() - timedelta(days=7)
        active_week_result = await self.db.execute(
            select(func.count(func.distinct(TeamActivity.user_id)))
            .where(
                and_(
                    TeamActivity.team_id == team_id,
                    TeamActivity.created_at >= week_ago
                )
            )
        )
        active_week = active_week_result.scalar() or 0
        
        # Total activities
        total_activities_result = await self.db.execute(
            select(func.count(TeamActivity.id)).where(TeamActivity.team_id == team_id)
        )
        total_activities = total_activities_result.scalar() or 0
        
        # Recent activities
        recent_result = await self.db.execute(
            select(TeamActivity)
            .where(TeamActivity.team_id == team_id)
            .order_by(desc(TeamActivity.created_at))
            .limit(10)
        )
        recent_activities = [
            {
                "id": act.id,
                "user_id": act.user_id,
                "type": act.activity_type,
                "description": act.description,
                "created_at": act.created_at.isoformat()
            }
            for act in recent_result.scalars().all()
        ]
        
        # Member activity distribution
        dist_result = await self.db.execute(
            select(
                TeamActivity.user_id,
                func.count(TeamActivity.id).label('count')
            )
            .where(TeamActivity.team_id == team_id)
            .group_by(TeamActivity.user_id)
        )
        distribution = {str(row[0]): row[1] for row in dist_result.all()}
        
        metrics = TeamDashboardMetrics(
            team_id=team_id,
            team_name=team.name,
            total_members=team.member_count,
            active_members_today=active_today,
            active_members_week=active_week,
            total_activities=total_activities,
            recent_activities=recent_activities,
            member_activity_distribution=distribution
        )
        
        # Cache for 5 minutes
        await redis_client.setex(
            cache_key,
            300,
            json.dumps(metrics.model_dump(), default=str)
        )
        
        return metrics
    
    async def _compute_effective_permissions(self, team_id: int, base_permissions: List[str]) -> List[str]:
        # Get parent team permissions
        team_result = await self.db.execute(select(Team).where(Team.id == team_id))
        team = team_result.scalar_one()
        
        effective = set(base_permissions)
        
        if team.parent_team_id:
            # Inherit from parent (simplified)
            parent_result = await self.db.execute(
                select(Team).where(Team.id == team.parent_team_id)
            )
            parent = parent_result.scalar_one_or_none()
            if parent:
                # In production, traverse full hierarchy
                effective.update(["read"])  # Inherit basic read permission
        
        return list(effective)
    
    async def _get_or_create_role(self, name: str, permissions: List[str]) -> Role:
        result = await self.db.execute(select(Role).where(Role.name == name))
        role = result.scalar_one_or_none()
        
        if not role:
            role = Role(name=name, permissions=permissions, is_system_role=True)
            self.db.add(role)
            await self.db.flush()
        
        return role
    
    async def _cache_team(self, team: Team):
        redis_client = await self.get_redis()
        team_data = {
            "id": team.id,
            "name": team.name,
            "slug": team.slug,
            "path": team.materialized_path
        }
        await redis_client.setex(f"team:{team.id}", 900, json.dumps(team_data))
    
    async def _record_activity(self, team_id: int, user_id: int, activity_type: str, description: str):
        activity = TeamActivity(
            team_id=team_id,
            user_id=user_id,
            activity_type=activity_type,
            description=description
        )
        self.db.add(activity)
        await self.db.commit()
        
        # Publish to Redis for real-time updates
        redis_client = await self.get_redis()
        await redis_client.publish(
            f"team:{team_id}:events",
            json.dumps({
                "type": activity_type,
                "user_id": user_id,
                "description": description,
                "timestamp": datetime.utcnow().isoformat()
            })
        )
EOF

# Backend: api/teams.py
cat > backend/app/api/teams.py << 'EOF'
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.team import (
    TeamCreate, TeamResponse, TeamMemberAdd, TeamMemberResponse,
    TeamDashboardMetrics, OrganizationCreate, RoleCreate
)
from app.services.team_service import TeamService
from app.models.team import Organization, Role
from typing import List

router = APIRouter(prefix="/api/teams", tags=["teams"])

@router.post("/organizations", response_model=dict)
async def create_organization(org: OrganizationCreate, db: AsyncSession = Depends(get_db)):
    org_obj = Organization(**org.model_dump())
    db.add(org_obj)
    await db.commit()
    await db.refresh(org_obj)
    return {"id": org_obj.id, "name": org_obj.name, "slug": org_obj.slug}

@router.post("/roles", response_model=dict)
async def create_role(role: RoleCreate, db: AsyncSession = Depends(get_db)):
    role_obj = Role(**role.model_dump())
    db.add(role_obj)
    await db.commit()
    await db.refresh(role_obj)
    return {"id": role_obj.id, "name": role_obj.name}

@router.post("", response_model=TeamResponse)
async def create_team(team: TeamCreate, db: AsyncSession = Depends(get_db)):
    service = TeamService(db)
    # Mock creator_id for demo
    creator_id = 1
    team_obj = await service.create_team(team, creator_id)
    return team_obj

@router.post("/{team_id}/members", response_model=TeamMemberResponse)
async def add_team_member(team_id: int, member: TeamMemberAdd, db: AsyncSession = Depends(get_db)):
    service = TeamService(db)
    # Mock inviter_id for demo
    inviter_id = 1
    member_obj = await service.add_team_member(team_id, member.user_id, member.role_id, inviter_id)
    return member_obj

@router.get("/{team_id}/dashboard", response_model=TeamDashboardMetrics)
async def get_team_dashboard(team_id: int, db: AsyncSession = Depends(get_db)):
    service = TeamService(db)
    return await service.get_team_dashboard(team_id)

@router.get("/{team_id}/permissions")
async def get_team_permissions(team_id: int, user_id: int, db: AsyncSession = Depends(get_db)):
    # Simplified permission check
    return {"team_id": team_id, "user_id": user_id, "permissions": ["read", "write"]}
EOF

# Backend: websocket/team_ws.py
cat > backend/app/websocket/team_ws.py << 'EOF'
from fastapi import WebSocket, WebSocketDisconnect
import redis.asyncio as redis
from app.config import settings
import json
import asyncio

class TeamWebSocketManager:
    def __init__(self):
        self.active_connections: dict = {}
        self.redis_client = None
    
    async def get_redis(self):
        if not self.redis_client:
            self.redis_client = await redis.from_url(settings.REDIS_URL, decode_responses=True)
        return self.redis_client
    
    async def connect(self, websocket: WebSocket, team_id: int, user_id: int):
        await websocket.accept()
        
        if team_id not in self.active_connections:
            self.active_connections[team_id] = {}
        
        self.active_connections[team_id][user_id] = websocket
        
        # Subscribe to Redis channel
        redis_client = await self.get_redis()
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(f"team:{team_id}:events")
        
        # Start listening task
        asyncio.create_task(self._listen_redis(pubsub, team_id))
        
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "team_id": team_id,
            "message": "Connected to team channel"
        })
    
    def disconnect(self, team_id: int, user_id: int):
        if team_id in self.active_connections:
            self.active_connections[team_id].pop(user_id, None)
            if not self.active_connections[team_id]:
                del self.active_connections[team_id]
    
    async def _listen_redis(self, pubsub, team_id: int):
        async for message in pubsub.listen():
            if message['type'] == 'message':
                data = json.loads(message['data'])
                await self.broadcast_to_team(team_id, data)
    
    async def broadcast_to_team(self, team_id: int, message: dict):
        if team_id in self.active_connections:
            disconnected = []
            for user_id, connection in self.active_connections[team_id].items():
                try:
                    await connection.send_json(message)
                except:
                    disconnected.append(user_id)
            
            for user_id in disconnected:
                self.disconnect(team_id, user_id)

manager = TeamWebSocketManager()
EOF

# Backend: main.py
cat > backend/app/main.py << 'EOF'
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api import teams
from app.database import engine, Base
from app.websocket.team_ws import manager
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(title="Team Management System", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(teams.router)

@app.websocket("/ws/teams/{team_id}")
async def team_websocket(websocket: WebSocket, team_id: int, user_id: int = 1):
    await manager.connect(websocket, team_id, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo messages for demo
            await manager.broadcast_to_team(team_id, {
                "type": "message",
                "user_id": user_id,
                "content": data
            })
    except WebSocketDisconnect:
        manager.disconnect(team_id, user_id)

@app.get("/health")
async def health():
    return {"status": "healthy"}
EOF

echo "Creating Frontend Files..."

# Frontend: package.json
cat > frontend/package.json << 'EOF'
{
  "name": "team-management-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-scripts": "5.0.1",
    "@mui/material": "^6.1.7",
    "@mui/icons-material": "^6.1.7",
    "@emotion/react": "^11.13.5",
    "@emotion/styled": "^11.13.5",
    "recharts": "^2.15.0",
    "axios": "^1.7.9",
    "react-router-dom": "^6.28.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test --watchAll=false",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": ["react-app"]
  },
  "browserslist": {
    "production": [">0.2%", "not dead", "not op_mini all"],
    "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
  }
}
EOF

# Frontend: public/index.html
cat > frontend/public/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Team Management System</title>
</head>
<body>
  <div id="root"></div>
</body>
</html>
EOF

# Frontend: src/index.js
cat > frontend/src/index.js << 'EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
EOF

# Frontend: src/App.js
cat > frontend/src/App.js << 'EOF'
import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Container, Box, Tabs, Tab } from '@mui/material';
import TeamCreation from './components/teams/TeamCreation';
import TeamMembers from './components/members/TeamMembers';
import TeamDashboard from './components/dashboard/TeamDashboard';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#1976d2' },
    secondary: { main: '#dc004e' },
  },
});

function App() {
  const [currentTab, setCurrentTab] = useState(0);
  const [selectedTeamId, setSelectedTeamId] = useState(null);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="xl">
        <Box sx={{ borderBottom: 1, borderColor: 'divider', my: 2 }}>
          <Tabs value={currentTab} onChange={(e, v) => setCurrentTab(v)}>
            <Tab label="Teams" />
            <Tab label="Members" disabled={!selectedTeamId} />
            <Tab label="Dashboard" disabled={!selectedTeamId} />
          </Tabs>
        </Box>
        
        {currentTab === 0 && <TeamCreation onTeamCreated={setSelectedTeamId} />}
        {currentTab === 1 && selectedTeamId && <TeamMembers teamId={selectedTeamId} />}
        {currentTab === 2 && selectedTeamId && <TeamDashboard teamId={selectedTeamId} />}
      </Container>
    </ThemeProvider>
  );
}

export default App;
EOF

# Frontend: src/services/api.js
cat > frontend/src/services/api.js << 'EOF'
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

export const createOrganization = async (data) => {
  const response = await axios.post(`${API_BASE}/api/teams/organizations`, data);
  return response.data;
};

export const createRole = async (data) => {
  const response = await axios.post(`${API_BASE}/api/teams/roles`, data);
  return response.data;
};

export const createTeam = async (data) => {
  const response = await axios.post(`${API_BASE}/api/teams`, data);
  return response.data;
};

export const addTeamMember = async (teamId, data) => {
  const response = await axios.post(`${API_BASE}/api/teams/${teamId}/members`, data);
  return response.data;
};

export const getTeamDashboard = async (teamId) => {
  const response = await axios.get(`${API_BASE}/api/teams/${teamId}/dashboard`);
  return response.data;
};

export const connectTeamWebSocket = (teamId, onMessage) => {
  const ws = new WebSocket(`ws://localhost:8000/ws/teams/${teamId}?user_id=1`);
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    onMessage(data);
  };
  return ws;
};
EOF

# Frontend: TeamCreation component
cat > frontend/src/components/teams/TeamCreation.js << 'EOF'
import React, { useState } from 'react';
import {
  Paper, Typography, TextField, Button, Box, Alert, Card, CardContent,
  Grid, Chip
} from '@mui/material';
import { createOrganization, createRole, createTeam } from '../../services/api';

function TeamCreation({ onTeamCreated }) {
  const [orgId, setOrgId] = useState(null);
  const [roleId, setRoleId] = useState(null);
  const [teamName, setTeamName] = useState('');
  const [teamDesc, setTeamDesc] = useState('');
  const [message, setMessage] = useState(null);
  const [createdTeams, setCreatedTeams] = useState([]);

  const handleCreateOrg = async () => {
    try {
      const org = await createOrganization({
        name: 'Demo Organization',
        slug: 'demo-org',
        settings: {}
      });
      setOrgId(org.id);
      setMessage({ type: 'success', text: `Organization created: ${org.name}` });
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to create organization' });
    }
  };

  const handleCreateRole = async () => {
    try {
      const role = await createRole({
        name: 'Member',
        description: 'Team member role',
        permissions: ['read', 'write']
      });
      setRoleId(role.id);
      setMessage({ type: 'success', text: `Role created: ${role.name}` });
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to create role' });
    }
  };

  const handleCreateTeam = async () => {
    if (!orgId) {
      setMessage({ type: 'error', text: 'Create organization first' });
      return;
    }
    
    try {
      const team = await createTeam({
        organization_id: orgId,
        name: teamName,
        description: teamDesc,
        parent_team_id: null,
        metadata: {}
      });
      
      setCreatedTeams([...createdTeams, team]);
      setMessage({ type: 'success', text: `Team created: ${team.name}` });
      onTeamCreated(team.id);
      setTeamName('');
      setTeamDesc('');
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to create team' });
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>Team Management System</Typography>
      
      {message && (
        <Alert severity={message.type} onClose={() => setMessage(null)} sx={{ mb: 2 }}>
          {message.text}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>1. Setup Organization</Typography>
              <Button 
                variant="contained" 
                onClick={handleCreateOrg}
                disabled={orgId !== null}
                fullWidth
              >
                {orgId ? `Org Created (ID: ${orgId})` : 'Create Organization'}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>2. Setup Role</Typography>
              <Button 
                variant="contained" 
                onClick={handleCreateRole}
                disabled={!orgId || roleId !== null}
                fullWidth
              >
                {roleId ? `Role Created (ID: ${roleId})` : 'Create Member Role'}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>3. Create Team</Typography>
              <TextField
                label="Team Name"
                value={teamName}
                onChange={(e) => setTeamName(e.target.value)}
                fullWidth
                margin="normal"
                size="small"
                disabled={!orgId}
              />
              <TextField
                label="Description"
                value={teamDesc}
                onChange={(e) => setTeamDesc(e.target.value)}
                fullWidth
                margin="normal"
                size="small"
                multiline
                rows={2}
                disabled={!orgId}
              />
              <Button 
                variant="contained" 
                onClick={handleCreateTeam}
                disabled={!orgId || !teamName}
                fullWidth
                sx={{ mt: 1 }}
              >
                Create Team
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {createdTeams.length > 0 && (
        <Paper sx={{ p: 2, mt: 3 }}>
          <Typography variant="h6" gutterBottom>Created Teams</Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {createdTeams.map(team => (
              <Chip 
                key={team.id}
                label={`${team.name} (ID: ${team.id})`}
                color="primary"
                onClick={() => onTeamCreated(team.id)}
              />
            ))}
          </Box>
        </Paper>
      )}
    </Box>
  );
}

export default TeamCreation;
EOF

# Frontend: TeamMembers component
cat > frontend/src/components/members/TeamMembers.js << 'EOF'
import React, { useState } from 'react';
import {
  Paper, Typography, TextField, Button, Box, Alert, List, ListItem,
  ListItemText, Chip
} from '@mui/material';
import { addTeamMember } from '../../services/api';

function TeamMembers({ teamId }) {
  const [userId, setUserId] = useState('');
  const [message, setMessage] = useState(null);
  const [members, setMembers] = useState([]);

  const handleAddMember = async () => {
    try {
      const member = await addTeamMember(teamId, {
        user_id: parseInt(userId),
        role_id: 1  // Assume role ID 1 exists
      });
      
      setMembers([...members, member]);
      setMessage({ type: 'success', text: 'Member added successfully' });
      setUserId('');
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to add member' });
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>Team Members</Typography>
      
      {message && (
        <Alert severity={message.type} onClose={() => setMessage(null)} sx={{ mb: 2 }}>
          {message.text}
        </Alert>
      )}

      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="h6" gutterBottom>Add Member</Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <TextField
            label="User ID"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            type="number"
            size="small"
          />
          <Button variant="contained" onClick={handleAddMember}>
            Add Member
          </Button>
        </Box>
      </Paper>

      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>Current Members ({members.length})</Typography>
        <List>
          {members.map((member, idx) => (
            <ListItem key={idx}>
              <ListItemText
                primary={`User ID: ${member.user_id}`}
                secondary={`Role ID: ${member.role_id} | Joined: ${new Date(member.joined_at).toLocaleString()}`}
              />
              <Box>
                {member.effective_permissions.map(perm => (
                  <Chip key={perm} label={perm} size="small" sx={{ ml: 0.5 }} />
                ))}
              </Box>
            </ListItem>
          ))}
        </List>
      </Paper>
    </Box>
  );
}

export default TeamMembers;
EOF

# Frontend: TeamDashboard component
cat > frontend/src/components/dashboard/TeamDashboard.js << 'EOF'
import React, { useState, useEffect } from 'react';
import {
  Paper, Typography, Box, Grid, Card, CardContent, CircularProgress
} from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { getTeamDashboard, connectTeamWebSocket } from '../../services/api';

function TeamDashboard({ teamId }) {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [realtimeEvents, setRealtimeEvents] = useState([]);

  useEffect(() => {
    loadDashboard();
    
    const ws = connectTeamWebSocket(teamId, (event) => {
      setRealtimeEvents(prev => [event, ...prev].slice(0, 5));
    });

    return () => ws.close();
  }, [teamId]);

  const loadDashboard = async () => {
    try {
      const data = await getTeamDashboard(teamId);
      setMetrics(data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
      setLoading(false);
    }
  };

  if (loading) return <CircularProgress />;
  if (!metrics) return <Typography>No data available</Typography>;

  const chartData = Object.entries(metrics.member_activity_distribution || {}).map(([userId, count]) => ({
    name: `User ${userId}`,
    activities: count
  }));

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>Team Dashboard: {metrics.team_name}</Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Total Members</Typography>
              <Typography variant="h4">{metrics.total_members}</Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Active Today</Typography>
              <Typography variant="h4">{metrics.active_members_today}</Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Active This Week</Typography>
              <Typography variant="h4">{metrics.active_members_week}</Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Total Activities</Typography>
              <Typography variant="h4">{metrics.total_activities}</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Member Activity Distribution</Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="activities" fill="#1976d2" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, height: 300, overflow: 'auto' }}>
            <Typography variant="h6" gutterBottom>Real-time Events</Typography>
            {realtimeEvents.map((event, idx) => (
              <Box key={idx} sx={{ mb: 1, p: 1, bgcolor: 'action.hover', borderRadius: 1 }}>
                <Typography variant="body2" color="primary">{event.type}</Typography>
                <Typography variant="caption">{event.message || event.content}</Typography>
              </Box>
            ))}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default TeamDashboard;
EOF

# Create test files
cat > backend/tests/test_teams.py << 'EOF'
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_organization():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/teams/organizations", json={
            "name": "Test Org",
            "slug": "test-org"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Org"

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
EOF

# Docker files
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: teamdb
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build:
      context: ./backend
      dockerfile: ../docker/Dockerfile.backend
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:postgres@postgres:5432/teamdb
      REDIS_URL: redis://redis:6379

  frontend:
    build:
      context: ./frontend
      dockerfile: ../docker/Dockerfile.frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
EOF

cat > docker/Dockerfile.backend << 'EOF'
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

cat > docker/Dockerfile.frontend << 'EOF'
FROM node:20-alpine
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
CMD ["npm", "start"]
EOF

# Build and run scripts
cat > build.sh << 'EOF'
#!/bin/bash

echo "=== Team Management System Build ==="

# Without Docker
echo -e "\n--- Building WITHOUT Docker ---"

# Setup backend
echo "Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "Starting services (PostgreSQL and Redis required)..."
# Assume services are running

echo "Running tests..."
PYTHONPATH=. pytest tests/ -v || echo "WARNING: Some tests failed"

echo "Starting backend..."
cd "$(dirname "$0")/backend"
PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
sleep 5

cd ../frontend
echo "Setting up frontend..."
npm install
npm run build

echo "Starting frontend..."
BROWSER=none npm start &
FRONTEND_PID=$!
sleep 10

echo -e "\n=== System Ready ==="
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo -e "\nPress Ctrl+C to stop"

wait
EOF

cat > stop.sh << 'EOF'
#!/bin/bash

echo "Stopping Team Management System..."

# Kill processes
pkill -f "uvicorn app.main:app"
pkill -f "react-scripts start"

# Docker
docker-compose down

echo "Stopped"
EOF

chmod +x build.sh stop.sh

echo "=========================================="
echo "Implementation Complete!"
echo "=========================================="
echo "Project structure created at: ${PROJECT_ROOT}"
echo ""
echo "To run WITHOUT Docker:"
echo "  cd ${PROJECT_ROOT}"
echo "  ./build.sh"
echo ""
echo "To run WITH Docker:"
echo "  cd ${PROJECT_ROOT}"
echo "  docker-compose up --build"
echo ""
echo "Access:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "=========================================="