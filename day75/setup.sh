#!/bin/bash

# Day 75: User Interface Components - Full Implementation Script
# This script creates a production-grade user management UI with React

set -e

PROJECT_NAME="user-management-ui"
BACKEND_PORT=8000
FRONTEND_PORT=3000

echo "=========================================="
echo "Day 75: User Interface Components"
echo "Creating User Management UI System"
echo "=========================================="

# Create project structure
create_project_structure() {
    echo "Creating project structure..."
    
    mkdir -p ${PROJECT_NAME}
    cd ${PROJECT_NAME}
    
    # Frontend structure
    mkdir -p frontend/src/{components,services,contexts,hooks,utils,pages,assets}
    mkdir -p frontend/src/components/{users,teams,permissions,profile,activity}
    mkdir -p frontend/public
    
    # Backend (from Day 74 - we'll create minimal version for testing)
    mkdir -p backend/app/{api,models,services,core}
    mkdir -p backend/tests
    
    # Docker
    mkdir -p docker
    
    # Tests
    mkdir -p tests/{unit,integration,e2e}
}

# Create Backend (minimal version connecting to Day 74 API)
create_backend() {
    echo "Creating backend server..."
    
    cat > backend/requirements.txt << 'EOF'
fastapi==0.115.0
uvicorn[standard]==0.32.0
sqlalchemy==2.0.35
asyncpg==0.30.0
pydantic==2.9.2
pydantic-settings==2.6.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.12
websockets==13.1
redis==5.2.0
pytest==8.3.3
pytest-asyncio==0.24.0
httpx==0.27.2
faker==30.8.2
EOF

    cat > backend/app/main.py << 'EOF'
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
EOF
}

# Create React Frontend
create_frontend() {
    echo "Creating React frontend..."
    
    cd frontend
    
    # Package.json
    cat > package.json << 'EOF'
{
  "name": "user-management-ui",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "@emotion/react": "^11.13.5",
    "@emotion/styled": "^11.13.5",
    "@mui/material": "^6.1.7",
    "@mui/icons-material": "^6.1.7",
    "@mui/x-data-grid": "^7.22.2",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.28.0",
    "react-window": "^1.8.10",
    "axios": "^1.7.9",
    "recharts": "^2.14.1",
    "date-fns": "^4.1.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.4",
    "vite": "^5.4.11",
    "@testing-library/react": "^16.0.1",
    "@testing-library/jest-dom": "^6.6.3",
    "vitest": "^2.1.8"
  },
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "test": "vitest"
  }
}
EOF

    # Vite config
    cat > vite.config.js << 'EOF'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': 'http://localhost:8000',
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true
      }
    }
  }
})
EOF

    # HTML template
    cat > index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>User Management System</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
EOF

    # Main entry point
    cat > src/main.jsx << 'EOF'
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </React.StrictMode>,
)
EOF

    # App component
    cat > src/App.jsx << 'EOF'
import React from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { AppBar, Toolbar, Typography, Container, Box, Drawer, List, ListItem, ListItemText, ListItemIcon } from '@mui/material'
import PeopleIcon from '@mui/icons-material/People'
import GroupsIcon from '@mui/icons-material/Groups'
import SecurityIcon from '@mui/icons-material/Security'
import PersonIcon from '@mui/icons-material/Person'
import TimelineIcon from '@mui/icons-material/Timeline'
import DashboardIcon from '@mui/icons-material/Dashboard'

import UserManagement from './pages/UserManagement'
import TeamManagement from './pages/TeamManagement'
import PermissionManagement from './pages/PermissionManagement'
import UserProfile from './pages/UserProfile'
import ActivityMonitor from './pages/ActivityMonitor'
import Dashboard from './pages/Dashboard'
import { WebSocketProvider } from './contexts/WebSocketContext'

const drawerWidth = 240

function App() {
  return (
    <WebSocketProvider>
      <Router>
        <Box sx={{ display: 'flex' }}>
          <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
            <Toolbar>
              <Typography variant="h6" noWrap component="div">
                User Management System
              </Typography>
            </Toolbar>
          </AppBar>
          
          <Drawer
            variant="permanent"
            sx={{
              width: drawerWidth,
              flexShrink: 0,
              '& .MuiDrawer-paper': { width: drawerWidth, boxSizing: 'border-box' },
            }}
          >
            <Toolbar />
            <Box sx={{ overflow: 'auto' }}>
              <List>
                <ListItem component={Link} to="/dashboard">
                  <ListItemIcon><DashboardIcon /></ListItemIcon>
                  <ListItemText primary="Dashboard" />
                </ListItem>
                <ListItem component={Link} to="/users">
                  <ListItemIcon><PeopleIcon /></ListItemIcon>
                  <ListItemText primary="Users" />
                </ListItem>
                <ListItem component={Link} to="/teams">
                  <ListItemIcon><GroupsIcon /></ListItemIcon>
                  <ListItemText primary="Teams" />
                </ListItem>
                <ListItem component={Link} to="/permissions">
                  <ListItemIcon><SecurityIcon /></ListItemIcon>
                  <ListItemText primary="Permissions" />
                </ListItem>
                <ListItem component={Link} to="/profile/1">
                  <ListItemIcon><PersonIcon /></ListItemIcon>
                  <ListItemText primary="Profile" />
                </ListItem>
                <ListItem component={Link} to="/activity">
                  <ListItemIcon><TimelineIcon /></ListItemIcon>
                  <ListItemText primary="Activity" />
                </ListItem>
              </List>
            </Box>
          </Drawer>
          
          <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
            <Toolbar />
            <Container maxWidth="xl">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/users" element={<UserManagement />} />
                <Route path="/teams" element={<TeamManagement />} />
                <Route path="/permissions" element={<PermissionManagement />} />
                <Route path="/profile/:userId" element={<UserProfile />} />
                <Route path="/activity" element={<ActivityMonitor />} />
              </Routes>
            </Container>
          </Box>
        </Box>
      </Router>
    </WebSocketProvider>
  )
}

export default App
EOF

    # WebSocket Context
    cat > src/contexts/WebSocketContext.jsx << 'EOF'
import React, { createContext, useContext, useEffect, useState, useRef } from 'react'

const WebSocketContext = createContext(null)

export const useWebSocket = () => useContext(WebSocketContext)

export const WebSocketProvider = ({ children }) => {
  const [isConnected, setIsConnected] = useState(false)
  const [messages, setMessages] = useState([])
  const ws = useRef(null)

  useEffect(() => {
    const connect = () => {
      ws.current = new WebSocket('ws://localhost:8000/ws')

      ws.current.onopen = () => {
        console.log('WebSocket connected')
        setIsConnected(true)
      }

      ws.current.onmessage = (event) => {
        const data = JSON.parse(event.data)
        setMessages(prev => [data, ...prev].slice(0, 100))
      }

      ws.current.onclose = () => {
        console.log('WebSocket disconnected')
        setIsConnected(false)
        setTimeout(connect, 3000)
      }

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error)
      }
    }

    connect()

    return () => {
      if (ws.current) {
        ws.current.close()
      }
    }
  }, [])

  const sendMessage = (message) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message))
    }
  }

  return (
    <WebSocketContext.Provider value={{ isConnected, messages, sendMessage }}>
      {children}
    </WebSocketContext.Provider>
  )
}
EOF

    # API Service
    cat > src/services/api.js << 'EOF'
import axios from 'axios'

const API_BASE = '/api'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const userAPI = {
  getAll: (params) => api.get('/users', { params }),
  getById: (id) => api.get(`/users/${id}`),
  create: (data) => api.post('/users', data),
  update: (id, data) => api.put(`/users/${id}`, data),
  delete: (id) => api.delete(`/users/${id}`),
}

export const teamAPI = {
  getAll: () => api.get('/teams'),
  create: (data) => api.post('/teams', data),
  addMember: (teamId, userId) => api.post(`/teams/${teamId}/members/${userId}`),
  removeMember: (teamId, userId) => api.delete(`/teams/${teamId}/members/${userId}`),
}

export const roleAPI = {
  getAll: () => api.get('/roles'),
  assign: (userId, roleId) => api.post(`/users/${userId}/roles/${roleId}`),
  revoke: (userId, roleId) => api.delete(`/users/${userId}/roles/${roleId}`),
}

export const activityAPI = {
  getAll: (params) => api.get('/activities', { params }),
}

export default api
EOF

    # User Management Page
    cat > src/pages/UserManagement.jsx << 'EOF'
import React, { useState, useEffect } from 'react'
import {
  Box, Paper, Typography, Button, TextField, MenuItem,
  Dialog, DialogTitle, DialogContent, DialogActions,
  Chip, Avatar, IconButton, Tooltip
} from '@mui/material'
import { DataGrid } from '@mui/x-data-grid'
import AddIcon from '@mui/icons-material/Add'
import EditIcon from '@mui/icons-material/Edit'
import DeleteIcon from '@mui/icons-material/Delete'
import SearchIcon from '@mui/icons-material/Search'
import { userAPI } from '../services/api'
import { useWebSocket } from '../contexts/WebSocketContext'

export default function UserManagement() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [roleFilter, setRoleFilter] = useState('all')
  const [openDialog, setOpenDialog] = useState(false)
  const [editUser, setEditUser] = useState(null)
  const [formData, setFormData] = useState({ email: '', name: '', avatar: '' })
  const { messages } = useWebSocket()

  useEffect(() => {
    loadUsers()
  }, [searchTerm, statusFilter, roleFilter])

  useEffect(() => {
    // Real-time updates via WebSocket
    const lastMessage = messages[0]
    if (lastMessage?.type === 'user_created' || lastMessage?.type === 'user_updated' || lastMessage?.type === 'user_deleted') {
      loadUsers()
    }
  }, [messages])

  const loadUsers = async () => {
    setLoading(true)
    try {
      const params = {}
      if (searchTerm) params.search = searchTerm
      if (statusFilter !== 'all') params.status = statusFilter
      if (roleFilter !== 'all') params.role = roleFilter
      
      const response = await userAPI.getAll(params)
      setUsers(response.data)
    } catch (error) {
      console.error('Failed to load users:', error)
    }
    setLoading(false)
  }

  const handleCreate = async () => {
    try {
      await userAPI.create(formData)
      setOpenDialog(false)
      setFormData({ email: '', name: '', avatar: '' })
      loadUsers()
    } catch (error) {
      console.error('Failed to create user:', error)
    }
  }

  const handleUpdate = async () => {
    try {
      await userAPI.update(editUser.id, formData)
      setOpenDialog(false)
      setEditUser(null)
      setFormData({ email: '', name: '', avatar: '' })
      loadUsers()
    } catch (error) {
      console.error('Failed to update user:', error)
    }
  }

  const handleDelete = async (id) => {
    if (window.confirm('Delete this user?')) {
      try {
        await userAPI.delete(id)
        loadUsers()
      } catch (error) {
        console.error('Failed to delete user:', error)
      }
    }
  }

  const columns = [
    {
      field: 'avatar',
      headerName: '',
      width: 70,
      renderCell: (params) => <Avatar src={params.value} alt={params.row.name} />,
    },
    { field: 'name', headerName: 'Name', width: 200 },
    { field: 'email', headerName: 'Email', width: 250 },
    {
      field: 'status',
      headerName: 'Status',
      width: 120,
      renderCell: (params) => (
        <Chip
          label={params.value}
          color={params.value === 'active' ? 'success' : 'default'}
          size="small"
        />
      ),
    },
    {
      field: 'roles',
      headerName: 'Roles',
      width: 200,
      renderCell: (params) => (
        <Box>
          {params.value.map((role) => (
            <Chip key={role} label={role} size="small" sx={{ mr: 0.5 }} />
          ))}
        </Box>
      ),
    },
    {
      field: 'teams',
      headerName: 'Teams',
      width: 200,
      renderCell: (params) => (
        <Box>
          {params.value.map((team) => (
            <Chip key={team} label={team} size="small" variant="outlined" sx={{ mr: 0.5 }} />
          ))}
        </Box>
      ),
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 120,
      renderCell: (params) => (
        <Box>
          <Tooltip title="Edit">
            <IconButton
              size="small"
              onClick={() => {
                setEditUser(params.row)
                setFormData({ name: params.row.name, email: params.row.email, avatar: params.row.avatar })
                setOpenDialog(true)
              }}
            >
              <EditIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Delete">
            <IconButton size="small" onClick={() => handleDelete(params.row.id)} color="error">
              <DeleteIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      ),
    },
  ]

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">User Management</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => {
            setEditUser(null)
            setFormData({ email: '', name: '', avatar: '' })
            setOpenDialog(true)
          }}
        >
          Add User
        </Button>
      </Box>

      <Paper sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <TextField
            placeholder="Search users..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: <SearchIcon sx={{ mr: 1, color: 'action.disabled' }} />,
            }}
            sx={{ flexGrow: 1 }}
          />
          <TextField
            select
            label="Status"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            sx={{ width: 150 }}
          >
            <MenuItem value="all">All</MenuItem>
            <MenuItem value="active">Active</MenuItem>
            <MenuItem value="inactive">Inactive</MenuItem>
          </TextField>
          <TextField
            select
            label="Role"
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            sx={{ width: 150 }}
          >
            <MenuItem value="all">All</MenuItem>
            <MenuItem value="Admin">Admin</MenuItem>
            <MenuItem value="Editor">Editor</MenuItem>
            <MenuItem value="Viewer">Viewer</MenuItem>
          </TextField>
        </Box>
      </Paper>

      <Paper sx={{ height: 600, width: '100%' }}>
        <DataGrid
          rows={users}
          columns={columns}
          pageSize={10}
          rowsPerPageOptions={[10, 25, 50]}
          loading={loading}
          disableSelectionOnClick
        />
      </Paper>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{editUser ? 'Edit User' : 'Create User'}</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Email"
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            margin="normal"
            disabled={!!editUser}
          />
          <TextField
            fullWidth
            label="Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Avatar URL"
            value={formData.avatar}
            onChange={(e) => setFormData({ ...formData, avatar: e.target.value })}
            margin="normal"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={editUser ? handleUpdate : handleCreate} variant="contained">
            {editUser ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
EOF

    # Team Management Page
    cat > src/pages/TeamManagement.jsx << 'EOF'
import React, { useState, useEffect } from 'react'
import {
  Box, Paper, Typography, Button, Grid, Card, CardContent, CardActions,
  List, ListItem, ListItemText, ListItemAvatar, Avatar, IconButton,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField,
  MenuItem, Select, FormControl, InputLabel
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import GroupsIcon from '@mui/icons-material/Groups'
import PersonAddIcon from '@mui/icons-material/PersonAdd'
import { teamAPI, userAPI } from '../services/api'
import { useWebSocket } from '../contexts/WebSocketContext'

export default function TeamManagement() {
  const [teams, setTeams] = useState([])
  const [users, setUsers] = useState([])
  const [selectedTeam, setSelectedTeam] = useState(null)
  const [openDialog, setOpenDialog] = useState(false)
  const [openAddMemberDialog, setOpenAddMemberDialog] = useState(false)
  const [selectedUserId, setSelectedUserId] = useState('')
  const [formData, setFormData] = useState({ name: '', description: '' })
  const { messages } = useWebSocket()

  useEffect(() => {
    loadTeams()
    loadUsers()
  }, [])

  useEffect(() => {
    const lastMessage = messages[0]
    if (lastMessage?.type?.startsWith('team_')) {
      loadTeams()
    }
  }, [messages])

  const loadTeams = async () => {
    try {
      const response = await teamAPI.getAll()
      setTeams(response.data)
    } catch (error) {
      console.error('Failed to load teams:', error)
    }
  }

  const loadUsers = async () => {
    try {
      const response = await userAPI.getAll({})
      setUsers(response.data)
    } catch (error) {
      console.error('Failed to load users:', error)
    }
  }

  const handleCreateTeam = async () => {
    try {
      await teamAPI.create(formData)
      setOpenDialog(false)
      setFormData({ name: '', description: '' })
      loadTeams()
    } catch (error) {
      console.error('Failed to create team:', error)
    }
  }

  const handleOpenAddMember = (team) => {
    setSelectedTeam(team)
    setOpenAddMemberDialog(true)
    setSelectedUserId('')
  }

  const handleAddMember = async () => {
    if (!selectedTeam || !selectedUserId) return
    
    try {
      await teamAPI.addMember(selectedTeam.id, selectedUserId)
      setOpenAddMemberDialog(false)
      setSelectedTeam(null)
      setSelectedUserId('')
      loadTeams()
    } catch (error) {
      console.error('Failed to add member:', error)
      alert('Failed to add member: ' + (error.response?.data?.detail || error.message))
    }
  }

  // Get all available users (backend handles duplicate prevention)
  const getAvailableUsers = () => {
    return users
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Team Management</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
        >
          Create Team
        </Button>
      </Box>

      <Grid container spacing={3}>
        {teams.map((team) => (
          <Grid item xs={12} md={6} lg={4} key={team.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <GroupsIcon sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="h6">{team.name}</Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {team.description}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {team.member_count} members
                </Typography>
              </CardContent>
              <CardActions>
                <Button 
                  size="small" 
                  startIcon={<PersonAddIcon />}
                  onClick={() => handleOpenAddMember(team)}
                >
                  Add Member
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create Team</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Team Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Description"
            multiline
            rows={3}
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            margin="normal"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateTeam} variant="contained">Create</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={openAddMemberDialog} onClose={() => setOpenAddMemberDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Member to {selectedTeam?.name}</DialogTitle>
        <DialogContent>
          <FormControl fullWidth margin="normal">
            <InputLabel>Select User</InputLabel>
            <Select
              value={selectedUserId}
              label="Select User"
              onChange={(e) => setSelectedUserId(e.target.value)}
            >
              {getAvailableUsers().map((user) => (
                <MenuItem key={user.id} value={user.id}>
                  {user.name} ({user.email})
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenAddMemberDialog(false)}>Cancel</Button>
          <Button 
            onClick={handleAddMember} 
            variant="contained"
            disabled={!selectedUserId}
          >
            Add Member
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
EOF

    # Permission Management Page
    cat > src/pages/PermissionManagement.jsx << 'EOF'
import React, { useState, useEffect } from 'react'
import {
  Box, Paper, Typography, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Switch, Chip
} from '@mui/material'
import { roleAPI, userAPI } from '../services/api'

export default function PermissionManagement() {
  const [users, setUsers] = useState([])
  const [roles, setRoles] = useState([])

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [usersRes, rolesRes] = await Promise.all([
        userAPI.getAll({}),
        roleAPI.getAll()
      ])
      setUsers(usersRes.data)
      setRoles(rolesRes.data)
    } catch (error) {
      console.error('Failed to load data:', error)
    }
  }

  const handleRoleToggle = async (userId, roleId, hasRole) => {
    try {
      if (hasRole) {
        await roleAPI.revoke(userId, roleId)
      } else {
        await roleAPI.assign(userId, roleId)
      }
      loadData()
    } catch (error) {
      console.error('Failed to toggle role:', error)
    }
  }

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3 }}>Permission Management</Typography>

      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>User</TableCell>
                <TableCell>Email</TableCell>
                {roles.map((role) => (
                  <TableCell key={role.id} align="center">
                    <Box>
                      <Typography variant="body2">{role.name}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {role.permission_count} perms
                      </Typography>
                    </Box>
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {users.map((user) => (
                <TableRow key={user.id}>
                  <TableCell>{user.name}</TableCell>
                  <TableCell>{user.email}</TableCell>
                  {roles.map((role) => {
                    const hasRole = user.roles.includes(role.name)
                    return (
                      <TableCell key={role.id} align="center">
                        <Switch
                          checked={hasRole}
                          onChange={() => handleRoleToggle(user.id, role.id, hasRole)}
                          color="primary"
                        />
                      </TableCell>
                    )
                  })}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  )
}
EOF

    # User Profile Page
    cat > src/pages/UserProfile.jsx << 'EOF'
import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import {
  Box, Paper, Typography, Avatar, Grid, Card, CardContent, Chip,
  List, ListItem, ListItemText, Divider
} from '@mui/material'
import { format } from 'date-fns'
import { userAPI, activityAPI } from '../services/api'

export default function UserProfile() {
  const { userId } = useParams()
  const [user, setUser] = useState(null)
  const [activities, setActivities] = useState([])

  useEffect(() => {
    loadProfile()
  }, [userId])

  const loadProfile = async () => {
    try {
      const [userRes, activityRes] = await Promise.all([
        userAPI.getById(userId),
        activityAPI.getAll({ user_id: userId, limit: 20 })
      ])
      setUser(userRes.data)
      setActivities(activityRes.data)
    } catch (error) {
      console.error('Failed to load profile:', error)
    }
  }

  if (!user) return <Typography>Loading...</Typography>

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3 }}>User Profile</Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Avatar
              src={user.avatar}
              alt={user.name}
              sx={{ width: 120, height: 120, mx: 'auto', mb: 2 }}
            />
            <Typography variant="h5">{user.name}</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              {user.email}
            </Typography>
            <Chip
              label={user.status}
              color={user.status === 'active' ? 'success' : 'default'}
              sx={{ mb: 2 }}
            />
            <Divider sx={{ my: 2 }} />
            <Box sx={{ textAlign: 'left' }}>
              <Typography variant="subtitle2" gutterBottom>Roles</Typography>
              <Box sx={{ mb: 2 }}>
                {user.roles.map((role) => (
                  <Chip key={role} label={role} size="small" sx={{ mr: 0.5, mb: 0.5 }} />
                ))}
              </Box>
              <Typography variant="subtitle2" gutterBottom>Teams</Typography>
              <Box>
                {user.teams.map((team) => (
                  <Chip key={team} label={team} size="small" variant="outlined" sx={{ mr: 0.5, mb: 0.5 }} />
                ))}
              </Box>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Recent Activity</Typography>
            <List>
              {activities.map((activity) => (
                <React.Fragment key={activity.id}>
                  <ListItem>
                    <ListItemText
                      primary={`${activity.action} ${activity.resource}`}
                      secondary={
                        <>
                          <Typography variant="body2" component="span">
                            {activity.details}
                          </Typography>
                          <br />
                          <Typography variant="caption" color="text.secondary">
                            {format(new Date(activity.timestamp), 'PPpp')}
                          </Typography>
                        </>
                      }
                    />
                  </ListItem>
                  <Divider />
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}
EOF

    # Dashboard Page
    cat > src/pages/Dashboard.jsx << 'EOF'
import React, { useState, useEffect } from 'react'
import {
  Box, Paper, Typography, Grid, Card, CardContent, Chip,
  LinearProgress, CircularProgress
} from '@mui/material'
import PeopleIcon from '@mui/icons-material/People'
import GroupsIcon from '@mui/icons-material/Groups'
import SecurityIcon from '@mui/icons-material/Security'
import TimelineIcon from '@mui/icons-material/Timeline'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import { userAPI, teamAPI, roleAPI, activityAPI } from '../services/api'
import { useWebSocket } from '../contexts/WebSocketContext'

export default function Dashboard() {
  const [metrics, setMetrics] = useState({
    totalUsers: 0,
    activeUsers: 0,
    inactiveUsers: 0,
    totalTeams: 0,
    totalRoles: 0,
    totalActivities: 0,
    loading: true
  })
  const { messages, isConnected } = useWebSocket()

  useEffect(() => {
    loadMetrics()
  }, [])

  useEffect(() => {
    // Refresh metrics when WebSocket messages arrive
    if (messages.length > 0) {
      loadMetrics()
    }
  }, [messages])

  const loadMetrics = async () => {
    try {
      const [usersRes, teamsRes, rolesRes, activitiesRes] = await Promise.all([
        userAPI.getAll({}),
        teamAPI.getAll(),
        roleAPI.getAll(),
        activityAPI.getAll({ limit: 1000 })
      ])

      const users = usersRes.data
      const activeUsers = users.filter(u => u.status === 'active').length
      const inactiveUsers = users.filter(u => u.status === 'inactive').length

      setMetrics({
        totalUsers: users.length,
        activeUsers,
        inactiveUsers,
        totalTeams: teamsRes.data.length,
        totalRoles: rolesRes.data.length,
        totalActivities: activitiesRes.data.length,
        loading: false
      })
    } catch (error) {
      console.error('Failed to load metrics:', error)
      setMetrics(prev => ({ ...prev, loading: false }))
    }
  }

  if (metrics.loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <CircularProgress />
      </Box>
    )
  }

  const metricCards = [
    {
      title: 'Total Users',
      value: metrics.totalUsers,
      icon: <PeopleIcon sx={{ fontSize: 40 }} />,
      color: '#1976d2',
      subtitle: `${metrics.activeUsers} active, ${metrics.inactiveUsers} inactive`
    },
    {
      title: 'Active Users',
      value: metrics.activeUsers,
      icon: <CheckCircleIcon sx={{ fontSize: 40 }} />,
      color: '#2e7d32',
      subtitle: `${metrics.totalUsers > 0 ? Math.round((metrics.activeUsers / metrics.totalUsers) * 100) : 0}% of total`
    },
    {
      title: 'Teams',
      value: metrics.totalTeams,
      icon: <GroupsIcon sx={{ fontSize: 40 }} />,
      color: '#ed6c02',
      subtitle: 'Total teams'
    },
    {
      title: 'Roles',
      value: metrics.totalRoles,
      icon: <SecurityIcon sx={{ fontSize: 40 }} />,
      color: '#9c27b0',
      subtitle: 'Total roles'
    },
    {
      title: 'Activities',
      value: metrics.totalActivities,
      icon: <TimelineIcon sx={{ fontSize: 40 }} />,
      color: '#d32f2f',
      subtitle: 'Total activities logged'
    }
  ]

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Dashboard</Typography>
        <Chip
          label={isConnected ? 'Live Updates' : 'Disconnected'}
          color={isConnected ? 'success' : 'error'}
          size="small"
        />
      </Box>

      <Grid container spacing={3}>
        {metricCards.map((card, index) => (
          <Grid item xs={12} sm={6} md={4} key={index}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Box>
                    <Typography color="text.secondary" gutterBottom variant="h6">
                      {card.title}
                    </Typography>
                    <Typography variant="h3" component="div" sx={{ fontWeight: 'bold', color: card.color }}>
                      {card.value}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      {card.subtitle}
                    </Typography>
                  </Box>
                  <Box sx={{ color: card.color, opacity: 0.7 }}>
                    {card.icon}
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Paper sx={{ mt: 3, p: 3 }}>
        <Typography variant="h6" gutterBottom>System Status</Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Typography variant="body2" color="text.secondary">WebSocket Connection</Typography>
            <Chip
              label={isConnected ? 'Connected' : 'Disconnected'}
              color={isConnected ? 'success' : 'error'}
              size="small"
              sx={{ mt: 1 }}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="body2" color="text.secondary">Data Freshness</Typography>
            <Typography variant="body1" sx={{ mt: 1 }}>
              Last updated: {new Date().toLocaleTimeString()}
            </Typography>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  )
}
EOF

    # Activity Monitor Page
    cat > src/pages/ActivityMonitor.jsx << 'EOF'
import React, { useState, useEffect } from 'react'
import {
  Box, Paper, Typography, List, ListItem, ListItemText, Chip, Avatar, ListItemAvatar
} from '@mui/material'
import { format } from 'date-fns'
import { activityAPI } from '../services/api'
import { useWebSocket } from '../contexts/WebSocketContext'

export default function ActivityMonitor() {
  const [activities, setActivities] = useState([])
  const { messages, isConnected } = useWebSocket()

  useEffect(() => {
    loadActivities()
  }, [])

  useEffect(() => {
    // Real-time activity updates
    if (messages.length > 0) {
      loadActivities()
    }
  }, [messages])

  const loadActivities = async () => {
    try {
      const response = await activityAPI.getAll({ limit: 50 })
      setActivities(response.data)
    } catch (error) {
      console.error('Failed to load activities:', error)
    }
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Activity Monitor</Typography>
        <Chip
          label={isConnected ? 'Live' : 'Disconnected'}
          color={isConnected ? 'success' : 'error'}
          size="small"
        />
      </Box>

      <Paper>
        <List>
          {activities.map((activity) => (
            <ListItem key={activity.id}>
              <ListItemAvatar>
                <Avatar sx={{ bgcolor: 'primary.main' }}>
                  {activity.user_name[0]}
                </Avatar>
              </ListItemAvatar>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="body1">{activity.user_name}</Typography>
                    <Chip label={activity.action} size="small" />
                    <Typography variant="body2" color="text.secondary">
                      {activity.resource}
                    </Typography>
                  </Box>
                }
                secondary={
                  <Box>
                    <Typography variant="body2">{activity.details}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {format(new Date(activity.timestamp), 'PPpp')}
                    </Typography>
                  </Box>
                }
              />
            </ListItem>
          ))}
        </List>
      </Paper>
    </Box>
  )
}
EOF

    cd ..
}

# Create Docker files
create_docker() {
    echo "Creating Docker configuration..."
    
    cat > docker/Dockerfile.backend << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

CMD ["python", "app/main.py"]
EOF

    cat > docker/Dockerfile.frontend << 'EOF'
FROM node:20-alpine as build

WORKDIR /app

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
EOF

    cat > docker/nginx.conf << 'EOF'
server {
    listen 80;
    server_name localhost;

    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: docker/Dockerfile.backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    environment:
      - PYTHONUNBUFFERED=1

  frontend:
    build:
      context: .
      dockerfile: docker/Dockerfile.frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
EOF
}

# Create build and run scripts
create_scripts() {
    echo "Creating build and run scripts..."
    
    cat > build.sh << 'EOF'
#!/bin/bash

set -e

echo "=== Building User Management UI System ==="

# Backend setup
echo "Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Frontend setup
echo "Setting up frontend..."
cd frontend
npm install
cd ..

echo "=== Build Complete ==="
echo ""
echo "To run without Docker:"
echo "  ./run.sh"
echo ""
echo "To run with Docker:"
echo "  docker-compose up --build"
EOF

    cat > run.sh << 'EOF'
#!/bin/bash

set -e

echo "=== Starting User Management UI System ==="

# Start backend
echo "Starting backend..."
cd backend
source venv/bin/activate
python app/main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo "Starting frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "=== System Started ==="
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
EOF

    cat > stop.sh << 'EOF'
#!/bin/bash

echo "Stopping all services..."
pkill -f "python app/main.py" || true
pkill -f "vite" || true
docker-compose down || true

echo "All services stopped"
EOF

    chmod +x build.sh run.sh stop.sh
}

# Create tests
create_tests() {
    echo "Creating tests..."
    
    cat > backend/tests/test_api.py << 'EOF'
import pytest
from fastapi.testclient import TestClient
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_get_users():
    response = client.get("/api/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_user():
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "avatar": "https://i.pravatar.cc/150"
    }
    response = client.post("/api/users", json=user_data)
    assert response.status_code == 200
    assert response.json()["email"] == user_data["email"]

def test_get_teams():
    response = client.get("/api/teams")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_roles():
    response = client.get("/api/roles")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_activities():
    response = client.get("/api/activities")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
EOF
}

# Main execution
main() {
    create_project_structure
    create_backend
    create_frontend
    create_docker
    create_scripts
    create_tests
    
    echo ""
    echo "=========================================="
    echo "Project created successfully!"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo "1. cd ${PROJECT_NAME}"
    echo "2. ./build.sh           # Install dependencies"
    echo "3. ./run.sh             # Start services"
    echo "4. Open http://localhost:3000"
    echo ""
    echo "Or use Docker:"
    echo "1. cd ${PROJECT_NAME}"
    echo "2. docker-compose up --build"
    echo ""
}

main