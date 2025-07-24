#!/bin/bash

# Day 15: Server Models Implementation Script
# Creates complete project structure, implements server models, builds, tests, and demos

set -e

echo "🚀 Day 15: Server Models Implementation Starting..."

# Create project structure
echo "📁 Creating project structure..."
mkdir -p server-management/{backend,frontend,docker,docs}
cd server-management

# Backend structure
mkdir -p backend/{app,tests,migrations,config}
mkdir -p backend/app/{models,api,core,db}

# Frontend structure  
mkdir -p frontend/{src,public,tests}
mkdir -p frontend/src/{components,pages,services,styles}

# Create backend requirements
echo "📦 Creating backend requirements..."
cat > backend/requirements.txt << 'EOF'
fastapi==0.110.0
uvicorn[standard]==0.29.0
sqlalchemy==2.0.28
alembic==1.13.1
psycopg2-binary==2.9.9
pydantic==2.6.3
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
pytest==8.1.1
pytest-asyncio==0.23.5
httpx==0.27.0
python-dotenv==1.0.1
EOF

# Create frontend package.json
echo "📦 Creating frontend package.json..."
cat > frontend/package.json << 'EOF'
{
  "name": "server-management-frontend",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.22.3",
    "axios": "^1.6.7",
    "recharts": "^2.12.2",
    "@headlessui/react": "^1.7.18",
    "@heroicons/react": "^2.1.1",
    "tailwindcss": "^3.4.1"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.1",
    "vite": "^5.1.6",
    "autoprefixer": "^10.4.18",
    "postcss": "^8.4.35"
  },
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "test": "vitest"
  }
}
EOF

# Database configuration
echo "🗄️ Creating database configuration..."
cat > backend/config/database.py << 'EOF'
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/serverdb")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
EOF

# Core server model
echo "🏗️ Creating server models..."
cat > backend/app/models/server.py << 'EOF'
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Table
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base
import uuid

# Association table for server tags
server_tags = Table('server_tags',
    Base.metadata,
    Column('server_id', UUID(as_uuid=True), ForeignKey('servers.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

class Server(Base):
    __tablename__ = "servers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    hostname = Column(String(255), nullable=False)
    ip_address = Column(String(45), nullable=False)  # Support IPv6
    port = Column(Integer, default=22)
    
    # Server specifications
    cpu_cores = Column(Integer)
    memory_gb = Column(Integer)
    storage_gb = Column(Integer)
    os_type = Column(String(50))
    os_version = Column(String(100))
    
    # Status and health
    status = Column(String(50), default="provisioning")  # provisioning, active, draining, terminated
    health_status = Column(String(50), default="unknown")  # healthy, degraded, failed, unknown
    last_heartbeat = Column(DateTime(timezone=True))
    
    # Categorization
    environment = Column(String(50))  # dev, staging, prod
    region = Column(String(50))
    availability_zone = Column(String(50))
    server_type = Column(String(50))  # web, database, cache, worker
    
    # Metadata and configuration
    metadata = Column(JSONB)
    configuration = Column(JSONB)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(255))
    
    # Relationships
    tags = relationship("Tag", secondary=server_tags, back_populates="servers")
    health_checks = relationship("HealthCheck", back_populates="server")
    dependencies = relationship("ServerDependency", foreign_keys="ServerDependency.server_id", back_populates="server")

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    category = Column(String(50))  # environment, service, version, custom
    color = Column(String(7), default="#3B82F6")  # Hex color
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    servers = relationship("Server", secondary=server_tags, back_populates="tags")

class HealthCheck(Base):
    __tablename__ = "health_checks"
    
    id = Column(Integer, primary_key=True)
    server_id = Column(UUID(as_uuid=True), ForeignKey('servers.id'), nullable=False)
    
    # Health metrics
    cpu_usage = Column(Integer)  # Percentage
    memory_usage = Column(Integer)  # Percentage  
    disk_usage = Column(Integer)  # Percentage
    network_latency = Column(Integer)  # Milliseconds
    
    # Application health
    service_status = Column(JSONB)  # Per-service health status
    error_count = Column(Integer, default=0)
    warning_count = Column(Integer, default=0)
    
    # Check metadata
    check_type = Column(String(50), default="automated")  # automated, manual
    status = Column(String(50))  # healthy, warning, critical
    message = Column(Text)
    
    checked_at = Column(DateTime(timezone=True), server_default=func.now())
    
    server = relationship("Server", back_populates="health_checks")

class ServerDependency(Base):
    __tablename__ = "server_dependencies"
    
    id = Column(Integer, primary_key=True)
    server_id = Column(UUID(as_uuid=True), ForeignKey('servers.id'), nullable=False)
    depends_on_id = Column(UUID(as_uuid=True), ForeignKey('servers.id'), nullable=False)
    
    dependency_type = Column(String(50))  # network, service, data, deployment
    description = Column(Text)
    is_critical = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    server = relationship("Server", foreign_keys=[server_id])
    depends_on = relationship("Server", foreign_keys=[depends_on_id])
EOF

# API schemas
echo "📋 Creating API schemas..."
cat > backend/app/api/schemas.py << 'EOF'
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class TagBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: str = "custom"
    color: str = "#3B82F6"

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class HealthCheckBase(BaseModel):
    cpu_usage: Optional[int] = Field(None, ge=0, le=100)
    memory_usage: Optional[int] = Field(None, ge=0, le=100)
    disk_usage: Optional[int] = Field(None, ge=0, le=100)
    network_latency: Optional[int] = Field(None, ge=0)
    service_status: Optional[Dict[str, Any]] = None
    error_count: int = 0
    warning_count: int = 0
    check_type: str = "automated"
    status: str = "healthy"
    message: Optional[str] = None

class HealthCheckCreate(HealthCheckBase):
    pass

class HealthCheck(HealthCheckBase):
    id: int
    server_id: UUID
    checked_at: datetime
    
    class Config:
        from_attributes = True

class ServerBase(BaseModel):
    name: str
    hostname: str
    ip_address: str
    port: int = 22
    cpu_cores: Optional[int] = None
    memory_gb: Optional[int] = None
    storage_gb: Optional[int] = None
    os_type: Optional[str] = None
    os_version: Optional[str] = None
    environment: Optional[str] = None
    region: Optional[str] = None
    availability_zone: Optional[str] = None
    server_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    configuration: Optional[Dict[str, Any]] = None

class ServerCreate(ServerBase):
    tag_ids: Optional[List[int]] = []

class ServerUpdate(BaseModel):
    name: Optional[str] = None
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    port: Optional[int] = None
    cpu_cores: Optional[int] = None
    memory_gb: Optional[int] = None
    storage_gb: Optional[int] = None
    os_type: Optional[str] = None
    os_version: Optional[str] = None
    status: Optional[str] = None
    health_status: Optional[str] = None
    environment: Optional[str] = None
    region: Optional[str] = None
    availability_zone: Optional[str] = None
    server_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    configuration: Optional[Dict[str, Any]] = None
    tag_ids: Optional[List[int]] = None

class Server(ServerBase):
    id: UUID
    status: str
    health_status: str
    last_heartbeat: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[str]
    tags: List[Tag] = []
    health_checks: List[HealthCheck] = []
    
    class Config:
        from_attributes = True
EOF

# API endpoints
echo "🔌 Creating API endpoints..."
cat > backend/app/api/servers.py << 'EOF'
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from config.database import get_db
from app.models.server import Server, Tag, HealthCheck
from app.api.schemas import (
    Server as ServerSchema, 
    ServerCreate, 
    ServerUpdate,
    Tag as TagSchema,
    TagCreate,
    HealthCheck as HealthCheckSchema,
    HealthCheckCreate
)

router = APIRouter(prefix="/api/servers", tags=["servers"])

@router.post("/", response_model=ServerSchema)
def create_server(server: ServerCreate, db: Session = Depends(get_db)):
    # Create server instance
    db_server = Server(**server.dict(exclude={'tag_ids'}))
    
    # Add tags if provided
    if server.tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(server.tag_ids)).all()
        db_server.tags = tags
    
    db.add(db_server)
    db.commit()
    db.refresh(db_server)
    return db_server

@router.get("/", response_model=List[ServerSchema])
def list_servers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    environment: Optional[str] = None,
    region: Optional[str] = None,
    status: Optional[str] = None,
    server_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Server)
    
    if environment:
        query = query.filter(Server.environment == environment)
    if region:
        query = query.filter(Server.region == region)
    if status:
        query = query.filter(Server.status == status)
    if server_type:
        query = query.filter(Server.server_type == server_type)
    
    return query.offset(skip).limit(limit).all()

@router.get("/{server_id}", response_model=ServerSchema)
def get_server(server_id: UUID, db: Session = Depends(get_db)):
    server = db.query(Server).filter(Server.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    return server

@router.put("/{server_id}", response_model=ServerSchema)
def update_server(server_id: UUID, server_update: ServerUpdate, db: Session = Depends(get_db)):
    server = db.query(Server).filter(Server.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    update_data = server_update.dict(exclude_unset=True, exclude={'tag_ids'})
    for field, value in update_data.items():
        setattr(server, field, value)
    
    # Update tags if provided
    if server_update.tag_ids is not None:
        tags = db.query(Tag).filter(Tag.id.in_(server_update.tag_ids)).all()
        server.tags = tags
    
    db.commit()
    db.refresh(server)
    return server

@router.post("/{server_id}/health", response_model=HealthCheckSchema)
def add_health_check(server_id: UUID, health_check: HealthCheckCreate, db: Session = Depends(get_db)):
    server = db.query(Server).filter(Server.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    db_health_check = HealthCheck(server_id=server_id, **health_check.dict())
    db.add(db_health_check)
    
    # Update server health status based on latest check
    if health_check.status == "critical":
        server.health_status = "failed"
    elif health_check.status == "warning":
        server.health_status = "degraded"
    else:
        server.health_status = "healthy"
    
    db.commit()
    db.refresh(db_health_check)
    return db_health_check

# Tag endpoints
@router.post("/tags/", response_model=TagSchema)
def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    db_tag = Tag(**tag.dict())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

@router.get("/tags/", response_model=List[TagSchema])
def list_tags(db: Session = Depends(get_db)):
    return db.query(Tag).all()
EOF

# Main FastAPI app
echo "⚡ Creating main FastAPI application..."
cat > backend/app/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.database import engine, Base
from app.api.servers import router as servers_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Server Management API",
    description="Distributed Systems Server Management API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(servers_router)

@app.get("/")
def read_root():
    return {"message": "Server Management API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "server-management-api"}
EOF

# Frontend components
echo "⚛️ Creating React components..."

# Main App component
cat > frontend/src/App.jsx << 'EOF'
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ServerDashboard from './pages/ServerDashboard';
import ServerDetail from './pages/ServerDetail';
import Layout from './components/Layout';
import './styles/global.css';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<ServerDashboard />} />
          <Route path="/servers/:id" element={<ServerDetail />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
EOF

# Server Dashboard
cat > frontend/src/pages/ServerDashboard.jsx << 'EOF'
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { PlusIcon, ServerIcon, CpuChipIcon } from '@heroicons/react/24/outline';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, PieChart, Pie, Cell } from 'recharts';
import { serverService } from '../services/api';

const COLORS = ['#10B981', '#F59E0B', '#EF4444', '#6B7280'];

function ServerDashboard() {
  const [servers, setServers] = useState([]);
  const [tags, setTags] = useState([]);
  const [filters, setFilters] = useState({
    environment: '',
    region: '',
    status: '',
    server_type: ''
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadServers();
    loadTags();
  }, [filters]);

  const loadServers = async () => {
    try {
      const data = await serverService.getServers(filters);
      setServers(data);
    } catch (error) {
      console.error('Failed to load servers:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadTags = async () => {
    try {
      const data = await serverService.getTags();
      setTags(data);
    } catch (error) {
      console.error('Failed to load tags:', error);
    }
  };

  const getStatusStats = () => {
    const stats = servers.reduce((acc, server) => {
      acc[server.status] = (acc[server.status] || 0) + 1;
      return acc;
    }, {});
    
    return Object.entries(stats).map(([status, count]) => ({
      name: status,
      value: count
    }));
  };

  const getRegionStats = () => {
    const stats = servers.reduce((acc, server) => {
      if (server.region) {
        acc[server.region] = (acc[server.region] || 0) + 1;
      }
      return acc;
    }, {});
    
    return Object.entries(stats).map(([region, count]) => ({
      region,
      count
    }));
  };

  const getHealthStatusColor = (status) => {
    switch (status) {
      case 'healthy': return 'text-green-600 bg-green-50';
      case 'degraded': return 'text-yellow-600 bg-yellow-50';
      case 'failed': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const statusStats = getStatusStats();
  const regionStats = getRegionStats();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Server Management</h1>
          <p className="text-gray-600">Monitor and manage your infrastructure</p>
        </div>
        <button className="btn-primary flex items-center space-x-2">
          <PlusIcon className="h-5 w-5" />
          <span>Add Server</span>
        </button>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <ServerIcon className="h-8 w-8 text-blue-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Servers</p>
              <p className="text-2xl font-bold text-gray-900">{servers.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <CpuChipIcon className="h-8 w-8 text-green-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Healthy Servers</p>
              <p className="text-2xl font-bold text-gray-900">
                {servers.filter(s => s.health_status === 'healthy').length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Status Distribution</h3>
          <PieChart width={200} height={150}>
            <Pie
              data={statusStats}
              cx={100}
              cy={75}
              innerRadius={30}
              outerRadius={60}
              dataKey="value"
            >
              {statusStats.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Servers by Region</h3>
          <BarChart width={400} height={250} data={regionStats}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="region" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="count" fill="#3B82F6" />
          </BarChart>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Filters</h3>
          <div className="grid grid-cols-2 gap-4">
            <select
              value={filters.environment}
              onChange={(e) => setFilters({...filters, environment: e.target.value})}
              className="input"
            >
              <option value="">All Environments</option>
              <option value="dev">Development</option>
              <option value="staging">Staging</option>
              <option value="prod">Production</option>
            </select>
            
            <select
              value={filters.status}
              onChange={(e) => setFilters({...filters, status: e.target.value})}
              className="input"
            >
              <option value="">All Statuses</option>
              <option value="active">Active</option>
              <option value="provisioning">Provisioning</option>
              <option value="draining">Draining</option>
              <option value="terminated">Terminated</option>
            </select>
          </div>
        </div>
      </div>

      {/* Server List */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Servers</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Server
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Health
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Environment
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Region
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tags
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {servers.map((server) => (
                <tr key={server.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <Link
                        to={`/servers/${server.id}`}
                        className="text-sm font-medium text-blue-600 hover:text-blue-500"
                      >
                        {server.name}
                      </Link>
                      <div className="text-sm text-gray-500">{server.hostname}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                      {server.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getHealthStatusColor(server.health_status)}`}>
                      {server.health_status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {server.environment}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {server.region}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex flex-wrap gap-1">
                      {server.tags?.slice(0, 3).map((tag) => (
                        <span
                          key={tag.id}
                          className="px-2 py-1 text-xs rounded"
                          style={{ backgroundColor: tag.color + '20', color: tag.color }}
                        >
                          {tag.name}
                        </span>
                      ))}
                      {server.tags?.length > 3 && (
                        <span className="px-2 py-1 text-xs rounded bg-gray-100 text-gray-600">
                          +{server.tags.length - 3}
                        </span>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default ServerDashboard;
EOF

# API Service
cat > frontend/src/services/api.js << 'EOF'
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const serverService = {
  getServers: async (filters = {}) => {
    const params = Object.entries(filters)
      .filter(([key, value]) => value)
      .reduce((acc, [key, value]) => ({ ...acc, [key]: value }), {});
    
    const response = await api.get('/api/servers/', { params });
    return response.data;
  },

  getServer: async (id) => {
    const response = await api.get(`/api/servers/${id}`);
    return response.data;
  },

  createServer: async (serverData) => {
    const response = await api.post('/api/servers/', serverData);
    return response.data;
  },

  updateServer: async (id, serverData) => {
    const response = await api.put(`/api/servers/${id}`, serverData);
    return response.data;
  },

  getTags: async () => {
    const response = await api.get('/api/servers/tags/');
    return response.data;
  },

  createTag: async (tagData) => {
    const response = await api.post('/api/servers/tags/', tagData);
    return response.data;
  },

  addHealthCheck: async (serverId, healthData) => {
    const response = await api.post(`/api/servers/${serverId}/health`, healthData);
    return response.data;
  },
};
EOF

# Layout component
cat > frontend/src/components/Layout.jsx << 'EOF'
import React from 'react';

function Layout({ children }) {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-xl font-bold text-blue-600">ServerOps</h1>
              </div>
            </div>
          </div>
        </div>
      </nav>
      
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  );
}

export default Layout;
EOF

# Global CSS
cat > frontend/src/styles/global.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer components {
  .btn-primary {
    @apply bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors;
  }
  
  .input {
    @apply block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500;
  }
  
  .card {
    @apply bg-white rounded-lg shadow-sm border border-gray-200 p-6;
  }
}
EOF

# Vite config
cat > frontend/vite.config.js << 'EOF'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true
  }
})
EOF

# Tailwind config
cat > frontend/tailwind.config.js << 'EOF'
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
EOF

# PostCSS config
cat > frontend/postcss.config.js << 'EOF'
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
EOF

# HTML template
cat > frontend/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Server Management Dashboard</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
EOF

# Main React entry
cat > frontend/src/main.jsx << 'EOF'
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
EOF

# Docker configurations
echo "🐳 Creating Docker configurations..."
cat > docker/docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: serverdb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d serverdb"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ../backend
      dockerfile: ../docker/Dockerfile.backend
    environment:
      DATABASE_URL: postgresql://user:password@postgres/serverdb
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ../backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ../frontend
      dockerfile: ../docker/Dockerfile.frontend
    ports:
      - "3000:3000"
    volumes:
      - ../frontend:/app
      - /app/node_modules
    command: npm run dev

volumes:
  postgres_data:
EOF

cat > docker/Dockerfile.backend << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

cat > docker/Dockerfile.frontend << 'EOF'
FROM node:18

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
EOF

# Test files
echo "🧪 Creating test files..."
cat > backend/tests/test_servers.py << 'EOF'
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.database import get_db, Base
from app.main import app

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_create_server():
    response = client.post(
        "/api/servers/",
        json={
            "name": "test-server-1",
            "hostname": "test.example.com",
            "ip_address": "192.168.1.100",
            "environment": "test",
            "region": "us-west-2"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test-server-1"
    assert "id" in data

def test_list_servers():
    response = client.get("/api/servers/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_server():
    # First create a server
    create_response = client.post(
        "/api/servers/",
        json={
            "name": "test-server-2",
            "hostname": "test2.example.com", 
            "ip_address": "192.168.1.101"
        }
    )
    server_id = create_response.json()["id"]
    
    # Then get it
    response = client.get(f"/api/servers/{server_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test-server-2"

def test_create_tag():
    response = client.post(
        "/api/servers/tags/",
        json={
            "name": "production",
            "description": "Production environment",
            "category": "environment",
            "color": "#DC2626"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "production"
EOF

# Environment setup
cat > backend/.env << 'EOF'
DATABASE_URL=postgresql://user:password@localhost/serverdb
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF

# Build and test script
echo "🔨 Building and testing..."

# Backend setup
echo "Setting up Python backend..."
cd backend
python -m venv venv
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate
pip install -r requirements.txt

# Run backend tests
echo "Running backend tests..."
python -m pytest tests/ -v

# Start backend in background for integration test
echo "Starting backend server..."
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
sleep 5

cd ../frontend

# Frontend setup
echo "Setting up React frontend..."
npm install

# Build frontend
echo "Building frontend..."
npm run build

# Start frontend development server
echo "Starting frontend development server..."
nohup npm run dev &
FRONTEND_PID=$!
sleep 10

# Integration test
echo "Running integration tests..."
curl -f http://localhost:8000/health || (echo "Backend health check failed" && exit 1)
curl -f http://localhost:3000 || (echo "Frontend health check failed" && exit 1)

# Create sample data
echo "Creating sample data..."
cd ..

curl -X POST "http://localhost:8000/api/servers/tags/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "production",
    "description": "Production environment",
    "category": "environment",
    "color": "#DC2626"
  }'

curl -X POST "http://localhost:8000/api/servers/tags/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "web-server",
    "description": "Web application server",
    "category": "service",
    "color": "#2563EB"
  }'

curl -X POST "http://localhost:8000/api/servers/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "web-01",
    "hostname": "web-01.example.com",
    "ip_address": "192.168.1.10",
    "environment": "prod",
    "region": "us-west-2",
    "server_type": "web",
    "cpu_cores": 4,
    "memory_gb": 16,
    "tag_ids": [1, 2]
  }'

curl -X POST "http://localhost:8000/api/servers/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "db-01",
    "hostname": "db-01.example.com",
    "ip_address": "192.168.1.20",
    "environment": "prod",
    "region": "us-west-2",
    "server_type": "database",
    "cpu_cores": 8,
    "memory_gb": 32
  }'

echo "✅ Implementation completed successfully!"
echo ""
echo "🌐 Access points:"
echo "- Frontend: http://localhost:3000"
echo "- Backend API: http://localhost:8000"
echo "- API Documentation: http://localhost:8000/docs"
echo ""
echo "📊 Demo features:"
echo "- Server dashboard with statistics"
echo "- Health monitoring visualization"
echo "- Tag-based filtering"
echo "- Regional distribution charts"
echo ""
echo "🏗️ To stop services:"
echo "kill $BACKEND_PID $FRONTEND_PID"

# Cleanup function
cleanup() {
    echo "Cleaning up background processes..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
}

trap cleanup EXIT

echo "Press Ctrl+C to stop all services..."
wait