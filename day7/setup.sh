#!/bin/bash

# Day 7: End-to-End Integration Implementation Script
# This script creates a complete full-stack application with health checks and integration

set -e  # Exit on any error

echo "🚀 Starting Day 7: End-to-End Integration Implementation"
echo "=================================================="

# Create project structure
echo "📁 Creating project structure..."
mkdir -p day7-integration/{backend/{app,tests},frontend/{src/{components,services},public},docker,docs}

cd day7-integration

# Backend setup
echo "🐍 Setting up Python backend..."

# Create backend requirements
cat > backend/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pydantic==2.5.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
alembic==1.12.1
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
pytest-cov==4.1.0
python-dotenv==1.0.0
structlog==23.2.0
prometheus-client==0.19.0
psutil==6.1.1
redis==5.0.1
celery==5.3.4
aioredis==2.0.1
EOF

# Create docker-compose.yml
echo "🐳 Creating Docker Compose configuration..."
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: docker/Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=development
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  frontend:
    build:
      context: .
      dockerfile: docker/Dockerfile.frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    environment:
      - REACT_APP_API_URL=http://localhost:8000

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  default:
    name: day7-integration
EOF

# Create Docker files
echo "🐳 Creating Docker configuration files..."

# Backend Dockerfile
cat > docker/Dockerfile.backend << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Frontend Dockerfile
cat > docker/Dockerfile.frontend << 'EOF'
FROM node:18-alpine as build

WORKDIR /app

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
EOF

# Nginx configuration
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
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

# Backend setup
echo "🐍 Setting up Python backend..."

# Create backend main application
cat > backend/app/main.py << 'EOF'
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import asyncio
import time
import psutil
from typing import Dict, Any
import os
from datetime import datetime

app = FastAPI(
    title="Day 7 Integration API",
    description="End-to-End Integration Demo",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demo
app_state = {
    "startup_time": datetime.now(),
    "request_count": 0,
    "hello_count": 0
}

@app.middleware("http")
async def count_requests(request, call_next):
    app_state["request_count"] += 1
    response = await call_next(request)
    return response

@app.get("/")
async def root():
    return {"message": "Day 7 Integration API is running!"}

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    try:
        # System metrics
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Uptime calculation
        uptime = datetime.now() - app_state["startup_time"]
        
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": int(uptime.total_seconds()),
            "system": {
                "memory_used_percent": memory.percent,
                "memory_available_mb": memory.available // (1024 * 1024),
                "cpu_percent": cpu_percent
            },
            "application": {
                "request_count": app_state["request_count"],
                "hello_count": app_state["hello_count"]
            },
            "dependencies": await check_dependencies()
        }
        
        return health_data
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

async def check_dependencies():
    """Check external dependencies"""
    deps = {}
    
    # Simulate database check
    try:
        await asyncio.sleep(0.1)  # Simulate DB query
        deps["database"] = {"status": "connected", "response_time_ms": 100}
    except Exception:
        deps["database"] = {"status": "error", "error": "Connection failed"}
    
    # Simulate Redis check
    try:
        await asyncio.sleep(0.05)  # Simulate Redis ping
        deps["redis"] = {"status": "connected", "response_time_ms": 50}
    except Exception:
        deps["redis"] = {"status": "error", "error": "Connection failed"}
    
    return deps

@app.get("/api/hello")
async def hello_world():
    """Hello World endpoint for frontend integration"""
    app_state["hello_count"] += 1
    
    return {
        "message": "Hello from the backend!",
        "timestamp": datetime.now().isoformat(),
        "count": app_state["hello_count"],
        "server_info": {
            "uptime_seconds": int((datetime.now() - app_state["startup_time"]).total_seconds()),
            "total_requests": app_state["request_count"]
        }
    }

@app.post("/api/echo")
async def echo_message(data: dict):
    """Echo endpoint for testing POST requests"""
    return {
        "echo": data,
        "processed_at": datetime.now().isoformat(),
        "message": "Data received and echoed back"
    }

@app.get("/api/status")
async def get_status():
    """Detailed application status"""
    return {
        "application": "Day 7 Integration Demo",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "startup_time": app_state["startup_time"].isoformat(),
        "metrics": {
            "total_requests": app_state["request_count"],
            "hello_requests": app_state["hello_count"]
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
EOF

# Create backend tests
cat > backend/tests/test_integration.py << 'EOF'
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "Day 7 Integration API is running!" in response.json()["message"]

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "system" in data
    assert "application" in data

def test_hello_world():
    response = client.get("/api/hello")
    assert response.status_code == 200
    data = response.json()
    assert "Hello from the backend!" in data["message"]
    assert "timestamp" in data
    assert "count" in data

def test_echo_endpoint():
    test_data = {"test": "data", "number": 123}
    response = client.post("/api/echo", json=test_data)
    assert response.status_code == 200
    data = response.json()
    assert data["echo"] == test_data

def test_status_endpoint():
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["application"] == "Day 7 Integration Demo"
    assert "metrics" in data
EOF

# Frontend setup
echo "⚛️  Setting up React frontend..."

# Create package.json
cat > frontend/package.json << 'EOF'
{
  "name": "day7-integration-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "axios": "^1.6.2",
    "web-vitals": "^3.5.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  },
  "proxy": "http://localhost:8000"
}
EOF

# Create main App component
cat > frontend/src/App.js << 'EOF'
import React, { useState, useEffect } from 'react';
import HealthDashboard from './components/HealthDashboard';
import HelloWorld from './components/HelloWorld';
import ApiTester from './components/ApiTester';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('health');

  return (
    <div className="App">
      <header className="App-header">
        <h1>Day 7: End-to-End Integration Demo</h1>
        <nav className="tab-navigation">
          <button 
            className={activeTab === 'health' ? 'active' : ''}
            onClick={() => setActiveTab('health')}
          >
            Health Dashboard
          </button>
          <button 
            className={activeTab === 'hello' ? 'active' : ''}
            onClick={() => setActiveTab('hello')}
          >
            Hello World
          </button>
          <button 
            className={activeTab === 'api' ? 'active' : ''}
            onClick={() => setActiveTab('api')}
          >
            API Tester
          </button>
        </nav>
      </header>

      <main className="App-main">
        {activeTab === 'health' && <HealthDashboard />}
        {activeTab === 'hello' && <HelloWorld />}
        {activeTab === 'api' && <ApiTester />}
      </main>
    </div>
  );
}

export default App;
EOF

# Create HealthDashboard component
cat > frontend/src/components/HealthDashboard.js << 'EOF'
import React, { useState, useEffect } from 'react';
import { getHealthStatus } from '../services/api';

const HealthDashboard = () => {
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchHealthData = async () => {
    try {
      const data = await getHealthStatus();
      setHealthData(data);
      setError(null);
      setLastUpdated(new Date());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealthData();
    const interval = setInterval(fetchHealthData, 5000); // Refresh every 5 seconds
    
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status) => {
    return status === 'healthy' || status === 'connected' ? '#4CAF50' : '#f44336';
  };

  if (loading) return <div className="loading">Loading health data...</div>;

  return (
    <div className="health-dashboard">
      <h2>System Health Dashboard</h2>
      
      {lastUpdated && (
        <p className="last-updated">
          Last updated: {lastUpdated.toLocaleTimeString()}
        </p>
      )}

      {error && (
        <div className="error-message">
          Error: {error}
        </div>
      )}

      {healthData && (
        <div className="health-grid">
          <div className="health-card">
            <h3>Overall Status</h3>
            <div 
              className="status-indicator"
              style={{ backgroundColor: getStatusColor(healthData.status) }}
            >
              {healthData.status.toUpperCase()}
            </div>
            <p>Uptime: {Math.floor(healthData.uptime_seconds / 60)} minutes</p>
          </div>

          <div className="health-card">
            <h3>System Resources</h3>
            <div className="metric">
              <span>Memory Usage:</span>
              <span>{healthData.system.memory_used_percent.toFixed(1)}%</span>
            </div>
            <div className="metric">
              <span>CPU Usage:</span>
              <span>{healthData.system.cpu_percent.toFixed(1)}%</span>
            </div>
            <div className="metric">
              <span>Available Memory:</span>
              <span>{healthData.system.memory_available_mb} MB</span>
            </div>
          </div>

          <div className="health-card">
            <h3>Application Metrics</h3>
            <div className="metric">
              <span>Total Requests:</span>
              <span>{healthData.application.request_count}</span>
            </div>
            <div className="metric">
              <span>Hello Requests:</span>
              <span>{healthData.application.hello_count}</span>
            </div>
          </div>

          <div className="health-card">
            <h3>Dependencies</h3>
            {Object.entries(healthData.dependencies).map(([name, info]) => (
              <div key={name} className="dependency">
                <span>{name}:</span>
                <span 
                  style={{ color: getStatusColor(info.status) }}
                  className="dependency-status"
                >
                  {info.status}
                  {info.response_time_ms && ` (${info.response_time_ms}ms)`}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default HealthDashboard;
EOF

# Create HelloWorld component
cat > frontend/src/components/HelloWorld.js << 'EOF'
import React, { useState } from 'react';
import { getHelloWorld } from '../services/api';

const HelloWorld = () => {
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleClick = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await getHelloWorld();
      setResponse(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="hello-world">
      <h2>Hello World Integration Test</h2>
      
      <button 
        onClick={handleClick} 
        disabled={loading}
        className="hello-button"
      >
        {loading ? 'Loading...' : 'Say Hello to Backend'}
      </button>

      {error && (
        <div className="error-message">
          Error: {error}
        </div>
      )}

      {response && (
        <div className="response-card">
          <h3>Backend Response:</h3>
          <div className="response-content">
            <p><strong>Message:</strong> {response.message}</p>
            <p><strong>Count:</strong> {response.count}</p>
            <p><strong>Timestamp:</strong> {new Date(response.timestamp).toLocaleString()}</p>
            
            <div className="server-info">
              <h4>Server Info:</h4>
              <p>Uptime: {Math.floor(response.server_info.uptime_seconds / 60)} minutes</p>
              <p>Total Requests: {response.server_info.total_requests}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HelloWorld;
EOF

# Create ApiTester component
cat > frontend/src/components/ApiTester.js << 'EOF'
import React, { useState } from 'react';
import { echoMessage, getStatus } from '../services/api';

const ApiTester = () => {
  const [echoInput, setEchoInput] = useState('{"test": "data"}');
  const [echoResponse, setEchoResponse] = useState(null);
  const [statusResponse, setStatusResponse] = useState(null);
  const [loading, setLoading] = useState({ echo: false, status: false });
  const [error, setError] = useState(null);

  const handleEcho = async () => {
    setLoading({ ...loading, echo: true });
    setError(null);
    
    try {
      const data = JSON.parse(echoInput);
      const response = await echoMessage(data);
      setEchoResponse(response);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading({ ...loading, echo: false });
    }
  };

  const handleStatus = async () => {
    setLoading({ ...loading, status: true });
    setError(null);
    
    try {
      const response = await getStatus();
      setStatusResponse(response);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading({ ...loading, status: false });
    }
  };

  return (
    <div className="api-tester">
      <h2>API Integration Tester</h2>

      <div className="test-section">
        <h3>Echo Test (POST)</h3>
        <textarea
          value={echoInput}
          onChange={(e) => setEchoInput(e.target.value)}
          rows={4}
          cols={50}
          placeholder="Enter JSON data to echo"
        />
        <br />
        <button 
          onClick={handleEcho} 
          disabled={loading.echo}
          className="test-button"
        >
          {loading.echo ? 'Sending...' : 'Send Echo Request'}
        </button>
        
        {echoResponse && (
          <div className="response-card">
            <h4>Echo Response:</h4>
            <pre>{JSON.stringify(echoResponse, null, 2)}</pre>
          </div>
        )}
      </div>

      <div className="test-section">
        <h3>Status Test (GET)</h3>
        <button 
          onClick={handleStatus} 
          disabled={loading.status}
          className="test-button"
        >
          {loading.status ? 'Loading...' : 'Get Server Status'}
        </button>
        
        {statusResponse && (
          <div className="response-card">
            <h4>Status Response:</h4>
            <pre>{JSON.stringify(statusResponse, null, 2)}</pre>
          </div>
        )}
      </div>

      {error && (
        <div className="error-message">
          Error: {error}
        </div>
      )}
    </div>
  );
};

export default ApiTester;
EOF

# Create API service
cat > frontend/src/services/api.js << 'EOF'
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    throw new Error(error.response?.data?.detail || error.message);
  }
);

export const getHealthStatus = async () => {
  const response = await apiClient.get('/health');
  return response.data;
};

export const getHelloWorld = async () => {
  const response = await apiClient.get('/api/hello');
  return response.data;
};

export const echoMessage = async (data) => {
  const response = await apiClient.post('/api/echo', data);
  return response.data;
};

export const getStatus = async () => {
  const response = await apiClient.get('/api/status');
  return response.data;
};

export default apiClient;
EOF

# Create CSS styles
cat > frontend/src/App.css << 'EOF'
.App {
  text-align: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.App-header {
  background-color: rgba(255, 255, 255, 0.1);
  padding: 20px;
  color: white;
}

.App-header h1 {
  margin: 0 0 20px 0;
  font-size: 2.5rem;
}

.tab-navigation {
  display: flex;
  justify-content: center;
  gap: 10px;
}

.tab-navigation button {
  padding: 10px 20px;
  border: none;
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  cursor: pointer;
  border-radius: 5px;
  transition: background-color 0.3s;
}

.tab-navigation button:hover {
  background-color: rgba(255, 255, 255, 0.3);
}

.tab-navigation button.active {
  background-color: rgba(255, 255, 255, 0.4);
  font-weight: bold;
}

.App-main {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.health-dashboard {
  background: white;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.health-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.health-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #e9ecef;
}

.health-card h3 {
  margin-top: 0;
  color: #333;
}

.status-indicator {
  display: inline-block;
  padding: 8px 16px;
  border-radius: 20px;
  color: white;
  font-weight: bold;
  margin: 10px 0;
}

.metric, .dependency {
  display: flex;
  justify-content: space-between;
  margin: 10px 0;
  padding: 5px 0;
  border-bottom: 1px solid #eee;
}

.dependency-status {
  font-weight: bold;
}

.hello-world, .api-tester {
  background: white;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.hello-button, .test-button {
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  margin: 10px;
  transition: transform 0.2s;
}

.hello-button:hover, .test-button:hover {
  transform: translateY(-2px);
}

.hello-button:disabled, .test-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.response-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin: 20px 0;
  text-align: left;
  border-left: 4px solid #667eea;
}

.response-content {
  margin-top: 10px;
}

.server-info {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #ddd;
}

.test-section {
  margin: 30px 0;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.test-section textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: monospace;
  margin: 10px 0;
}

.error-message {
  background: #f8d7da;
  color: #721c24;
  padding: 12px;
  border-radius: 4px;
  margin: 10px 0;
  border: 1px solid #f5c6cb;
}

.loading {
  color: #666;
  font-style: italic;
  padding: 20px;
}

.last-updated {
  color: #666;
  font-size: 0.9em;
  margin-bottom: 20px;
}

pre {
  background: #f4f4f4;
  padding: 15px;
  border-radius: 4px;
  overflow-x: auto;
  text-align: left;
}
EOF

# Create index.js
cat > frontend/src/index.js << 'EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
EOF

# Create public/index.html
cat > frontend/public/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="Day 7 End-to-End Integration Demo" />
    <title>Day 7 Integration Demo</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
EOF

# Create Docker-related instructions to README
echo "📝 Updating README with Docker instructions..."
cat >> README.md << 'EOF'

## Docker Setup

To run the application using Docker:

1. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

2. Access the applications:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

3. Stop the containers:
   ```bash
   docker-compose down
   ```

The application includes:
- Frontend (React) served by Nginx
- Backend (FastAPI) with health checks
- Redis for caching and session management
EOF

echo "✅ Setup complete! You can now run the application using Docker Compose."
echo "🚀 To start: docker-compose up --build"
echo "🌐 Frontend will be available at: http://localhost:3000"
echo "🔧 Backend API will be available at: http://localhost:8000"