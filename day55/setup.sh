#!/bin/bash

# Day 55: Real-time UI Components - Complete Implementation Script
# This script creates a full real-time UI dashboard with live components

set -e

PROJECT_NAME="realtime-ui-components"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR/$PROJECT_NAME"

echo "=================================="
echo "Day 55: Real-time UI Components"
echo "=================================="

# Clean up existing project
if [ -d "$PROJECT_DIR" ]; then
    echo "Removing existing project..."
    rm -rf "$PROJECT_DIR"
fi

# Create project structure
echo "Creating project structure..."
mkdir -p "$PROJECT_DIR"/{backend,frontend,tests,docker}
cd "$PROJECT_DIR"

# Create backend structure
mkdir -p backend/{app,tests}
mkdir -p backend/app/{models,routes,services,websocket}

# Create frontend structure
mkdir -p frontend/src/{components,contexts,hooks,services,utils,styles}
mkdir -p frontend/src/components/{charts,indicators,controls}
mkdir -p frontend/public

# ============================================
# BACKEND FILES
# ============================================

# Backend requirements.txt
cat > backend/requirements.txt << 'EOF'
fastapi==0.115.0
uvicorn[standard]==0.32.0
websockets==13.1
python-socketio==5.11.4
redis==5.2.0
aioredis==2.0.1
pydantic==2.9.2
python-dotenv==1.0.1
pytest==8.3.3
pytest-asyncio==0.24.0
httpx==0.27.2
faker==30.3.0
EOF

# Backend main application
cat > backend/app/main.py << 'EOF'
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import json
import time
import random
from datetime import datetime
from typing import Dict, Set
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store active connections
active_connections: Set[WebSocket] = set()
connection_quality: Dict[str, dict] = {}

# Metrics storage
metrics = {
    "user_count": 0,
    "message_rate": 0,
    "messages_history": [],
    "latency_history": []
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start background tasks
    task1 = asyncio.create_task(simulate_user_activity())
    task2 = asyncio.create_task(simulate_message_traffic())
    task3 = asyncio.create_task(broadcast_metrics())
    yield
    # Cleanup
    task1.cancel()
    task2.cancel()
    task3.cancel()

app = FastAPI(title="Real-time UI Components", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def simulate_user_activity():
    """Simulate user count changes"""
    while True:
        await asyncio.sleep(2)
        # Simulate user count fluctuation
        change = random.randint(-5, 10)
        metrics["user_count"] = max(50, min(500, metrics["user_count"] + change))
        
        await broadcast_message({
            "type": "user_count",
            "data": {
                "count": metrics["user_count"],
                "timestamp": datetime.now().isoformat()
            }
        })

async def simulate_message_traffic():
    """Simulate message traffic for rate calculations"""
    while True:
        await asyncio.sleep(0.5)
        # Generate random message burst
        messages = random.randint(10, 50)
        timestamp = time.time()
        
        metrics["messages_history"].append({
            "count": messages,
            "timestamp": timestamp
        })
        
        # Keep only last 60 seconds
        cutoff = timestamp - 60
        metrics["messages_history"] = [
            m for m in metrics["messages_history"] 
            if m["timestamp"] > cutoff
        ]
        
        # Calculate rate
        total_messages = sum(m["count"] for m in metrics["messages_history"])
        metrics["message_rate"] = total_messages / 60
        
        await broadcast_message({
            "type": "message_rate",
            "data": {
                "rate": round(metrics["message_rate"], 2),
                "timestamp": datetime.now().isoformat()
            }
        })

async def broadcast_metrics():
    """Broadcast aggregated metrics periodically"""
    while True:
        await asyncio.sleep(1)
        
        # Simulate latency
        latency = random.randint(20, 100) + (random.random() * 50 if random.random() > 0.8 else 0)
        metrics["latency_history"].append(latency)
        if len(metrics["latency_history"]) > 20:
            metrics["latency_history"].pop(0)
        
        await broadcast_message({
            "type": "metrics",
            "data": {
                "user_count": metrics["user_count"],
                "message_rate": round(metrics["message_rate"], 2),
                "latency": round(latency, 2),
                "timestamp": datetime.now().isoformat()
            }
        })

async def broadcast_message(message: dict):
    """Broadcast message to all connected clients"""
    disconnected = set()
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except Exception as e:
            logger.error(f"Error broadcasting to client: {e}")
            disconnected.add(connection)
    
    # Remove disconnected clients
    for conn in disconnected:
        active_connections.discard(conn)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    client_id = id(websocket)
    
    logger.info(f"Client {client_id} connected. Total: {len(active_connections)}")
    
    # Send initial state
    await websocket.send_json({
        "type": "connection",
        "data": {
            "status": "connected",
            "client_id": client_id,
            "timestamp": datetime.now().isoformat()
        }
    })
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "ping":
                # Respond to ping with pong
                await websocket.send_json({
                    "type": "pong",
                    "data": {
                        "timestamp": datetime.now().isoformat(),
                        "latency": data.get("data", {}).get("client_timestamp")
                    }
                })
            elif data.get("type") == "message":
                # Echo message back with confirmation
                await websocket.send_json({
                    "type": "message_ack",
                    "data": {
                        "id": data.get("data", {}).get("id"),
                        "status": "delivered",
                        "timestamp": datetime.now().isoformat()
                    }
                })
                
    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected")
    except Exception as e:
        logger.error(f"Error in websocket: {e}")
    finally:
        active_connections.discard(websocket)
        logger.info(f"Client {client_id} removed. Total: {len(active_connections)}")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "connections": len(active_connections),
        "metrics": {
            "user_count": metrics["user_count"],
            "message_rate": round(metrics["message_rate"], 2)
        }
    }

@app.get("/api/stats")
async def get_stats():
    """REST endpoint for stats (fallback when WebSocket unavailable)"""
    return {
        "user_count": metrics["user_count"],
        "message_rate": round(metrics["message_rate"], 2),
        "latency": round(sum(metrics["latency_history"]) / len(metrics["latency_history"]), 2) if metrics["latency_history"] else 0,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

# ============================================
# FRONTEND FILES
# ============================================

# Frontend package.json
cat > frontend/package.json << 'EOF'
{
  "name": "realtime-ui-components",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "recharts": "^2.15.0",
    "lucide-react": "^0.460.0",
    "@tanstack/react-query": "^5.62.0",
    "axios": "^1.7.9"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.4",
    "vite": "^6.0.3",
    "@types/react": "^18.3.12",
    "@types/react-dom": "^18.3.1"
  },
  "scripts": {
    "dev": "vite --host 0.0.0.0 --port 3000",
    "build": "vite build",
    "preview": "vite preview"
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
    host: '0.0.0.0',
    port: 3000,
    proxy: {
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true
      },
      '/api': {
        target: 'http://localhost:8000'
      }
    }
  }
})
EOF

# Frontend index.html
cat > frontend/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Real-time UI Dashboard</title>
</head>
<body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
</body>
</html>
EOF

# Frontend main entry
cat > frontend/src/main.jsx << 'EOF'
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './styles/index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
EOF

# Main App component
cat > frontend/src/App.jsx << 'EOF'
import React from 'react';
import { RealtimeProvider } from './contexts/RealtimeContext';
import Dashboard from './components/Dashboard';

function App() {
  return (
    <RealtimeProvider>
      <Dashboard />
    </RealtimeProvider>
  );
}

export default App;
EOF

# Realtime Context
cat > frontend/src/contexts/RealtimeContext.jsx << 'EOF'
import React, { createContext, useContext, useEffect, useReducer, useCallback, useRef } from 'react';

const RealtimeContext = createContext();

const initialState = {
  connectionStatus: 'connecting',
  latency: 0,
  lastUpdate: null,
  userCount: 0,
  messageRate: 0,
  offlineQueue: [],
  data: {}
};

function realtimeReducer(state, action) {
  switch (action.type) {
    case 'SET_CONNECTION_STATUS':
      return { ...state, connectionStatus: action.payload };
    case 'SET_LATENCY':
      return { ...state, latency: action.payload };
    case 'SET_LAST_UPDATE':
      return { ...state, lastUpdate: action.payload };
    case 'UPDATE_DATA':
      return {
        ...state,
        data: { ...state.data, ...action.payload },
        lastUpdate: new Date().toISOString()
      };
    case 'SET_USER_COUNT':
      return { ...state, userCount: action.payload };
    case 'SET_MESSAGE_RATE':
      return { ...state, messageRate: action.payload };
    case 'ADD_TO_QUEUE':
      return {
        ...state,
        offlineQueue: [...state.offlineQueue, action.payload]
      };
    case 'CLEAR_QUEUE':
      return { ...state, offlineQueue: [] };
    default:
      return state;
  }
}

export function RealtimeProvider({ children }) {
  const [state, dispatch] = useReducer(realtimeReducer, initialState);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttempts = useRef(0);
  const pingIntervalRef = useRef(null);
  const offlineQueueRef = useRef([]);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    dispatch({ type: 'SET_CONNECTION_STATUS', payload: 'connecting' });

    // Use proxy path for WebSocket connection (Vite will proxy to backend)
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket connected');
      dispatch({ type: 'SET_CONNECTION_STATUS', payload: 'connected' });
      reconnectAttempts.current = 0;

      // Start ping interval
      pingIntervalRef.current = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          const start = Date.now();
          ws.send(JSON.stringify({
            type: 'ping',
            data: { client_timestamp: start }
          }));
        }
      }, 5000);

      // Process offline queue
      if (offlineQueueRef.current.length > 0) {
        offlineQueueRef.current.forEach(msg => {
          ws.send(JSON.stringify(msg));
        });
        offlineQueueRef.current = [];
        dispatch({ type: 'CLEAR_QUEUE' });
      }
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);

      if (message.type === 'pong') {
        const latency = Date.now() - message.data.latency;
        dispatch({ type: 'SET_LATENCY', payload: latency });
      } else if (message.type === 'user_count') {
        dispatch({ type: 'SET_USER_COUNT', payload: message.data.count });
      } else if (message.type === 'message_rate') {
        dispatch({ type: 'SET_MESSAGE_RATE', payload: message.data.rate });
      } else if (message.type === 'metrics') {
        dispatch({ type: 'UPDATE_DATA', payload: message.data });
      }

      dispatch({ type: 'SET_LAST_UPDATE', payload: new Date().toISOString() });
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      // Don't set status here, let onclose handle it
    };

    ws.onclose = (event) => {
      console.log('WebSocket closed', event.code, event.reason);
      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current);
        pingIntervalRef.current = null;
      }

      // Only reconnect if not intentionally closed (code 1000 = normal closure)
      // Also check if wsRef still points to this connection
      if (event.code !== 1000 && wsRef.current === ws) {
        dispatch({ type: 'SET_CONNECTION_STATUS', payload: 'reconnecting' });

        // Exponential backoff
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
        reconnectAttempts.current++;

        if (reconnectAttempts.current > 5) {
          dispatch({ type: 'SET_CONNECTION_STATUS', payload: 'offline' });
        } else {
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        }
      } else if (event.code === 1000) {
        // Normal closure, set status to offline
        dispatch({ type: 'SET_CONNECTION_STATUS', payload: 'offline' });
      }
    };
  }, []);

  useEffect(() => {
    // Small delay to ensure backend is ready
    const connectTimeout = setTimeout(() => {
      connect();
    }, 100);

    return () => {
      clearTimeout(connectTimeout);
      if (wsRef.current) {
        wsRef.current.close(1000, 'Component unmounting');
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current);
      }
    };
  }, [connect]);

  const sendMessage = useCallback((message) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      // Queue for later
      offlineQueueRef.current.push(message);
      dispatch({ type: 'ADD_TO_QUEUE', payload: message });
    }
  }, []);

  const value = {
    ...state,
    sendMessage,
    reconnect: connect
  };

  return (
    <RealtimeContext.Provider value={value}>
      {children}
    </RealtimeContext.Provider>
  );
}

export function useRealtime() {
  const context = useContext(RealtimeContext);
  if (!context) {
    throw new Error('useRealtime must be used within RealtimeProvider');
  }
  return context;
}
EOF

# Dashboard component
cat > frontend/src/components/Dashboard.jsx << 'EOF'
import React, { useState } from 'react';
import { useRealtime } from '../contexts/RealtimeContext';
import ConnectionStatus from './indicators/ConnectionStatus';
import LiveUserCount from './charts/LiveUserCount';
import MessageRateChart from './charts/MessageRateChart';
import OfflineQueueIndicator from './indicators/OfflineQueueIndicator';
import AutoRefreshControl from './controls/AutoRefreshControl';
import '../styles/dashboard.css';

function Dashboard() {
  const { connectionStatus } = useRealtime();
  const [autoRefresh, setAutoRefresh] = useState(true);

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Real-time UI Dashboard</h1>
        <div className="header-controls">
          <AutoRefreshControl enabled={autoRefresh} onToggle={setAutoRefresh} />
          <ConnectionStatus />
        </div>
      </header>

      <div className="dashboard-grid">
        <div className="dashboard-card">
          <h2>Active Users</h2>
          <LiveUserCount />
        </div>

        <div className="dashboard-card">
          <h2>Message Rate</h2>
          <MessageRateChart />
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="dashboard-card full-width">
          <h2>System Status</h2>
          <OfflineQueueIndicator />
        </div>
      </div>

      {connectionStatus === 'offline' && (
        <div className="offline-banner">
          You're currently offline. Actions will be queued and sent when connection is restored.
        </div>
      )}
    </div>
  );
}

export default Dashboard;
EOF

# Connection Status Indicator
cat > frontend/src/components/indicators/ConnectionStatus.jsx << 'EOF'
import React from 'react';
import { useRealtime } from '../../contexts/RealtimeContext';
import { Wifi, WifiOff, RefreshCw } from 'lucide-react';

function ConnectionStatus() {
  const { connectionStatus, latency, lastUpdate, reconnect } = useRealtime();

  const getStatusConfig = () => {
    switch (connectionStatus) {
      case 'connected':
        return {
          icon: Wifi,
          color: '#10b981',
          text: 'Connected',
          detail: latency ? `${Math.round(latency)}ms latency` : ''
        };
      case 'connecting':
        return {
          icon: RefreshCw,
          color: '#f59e0b',
          text: 'Connecting...',
          detail: ''
        };
      case 'reconnecting':
        return {
          icon: RefreshCw,
          color: '#f59e0b',
          text: 'Reconnecting...',
          detail: 'Attempting to restore connection'
        };
      case 'offline':
        return {
          icon: WifiOff,
          color: '#ef4444',
          text: 'Offline',
          detail: 'No connection'
        };
      default:
        return {
          icon: WifiOff,
          color: '#6b7280',
          text: 'Unknown',
          detail: ''
        };
    }
  };

  const config = getStatusConfig();
  const Icon = config.icon;

  const formatLastUpdate = (timestamp) => {
    if (!timestamp) return 'Never';
    const diff = Date.now() - new Date(timestamp).getTime();
    if (diff < 1000) return 'Just now';
    if (diff < 60000) return `${Math.floor(diff / 1000)}s ago`;
    return `${Math.floor(diff / 60000)}m ago`;
  };

  return (
    <div className="connection-status">
      <div className="status-indicator" style={{ backgroundColor: config.color }}>
        <Icon size={16} className={connectionStatus === 'reconnecting' ? 'spinning' : ''} />
      </div>
      <div className="status-details">
        <div className="status-text">{config.text}</div>
        {config.detail && <div className="status-detail">{config.detail}</div>}
        <div className="status-update">Last: {formatLastUpdate(lastUpdate)}</div>
      </div>
      {connectionStatus === 'offline' && (
        <button onClick={reconnect} className="reconnect-btn">
          Retry
        </button>
      )}
    </div>
  );
}

export default ConnectionStatus;
EOF

# Live User Count
cat > frontend/src/components/charts/LiveUserCount.jsx << 'EOF'
import React, { useState, useEffect } from 'react';
import { useRealtime } from '../../contexts/RealtimeContext';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { Users } from 'lucide-react';

function LiveUserCount() {
  const { userCount, connectionStatus } = useRealtime();
  const [history, setHistory] = useState([]);

  useEffect(() => {
    if (userCount > 0) {
      setHistory(prev => {
        const newHistory = [
          ...prev,
          { time: new Date().getTime(), count: userCount }
        ];
        // Keep last 20 data points
        return newHistory.slice(-20);
      });
    }
  }, [userCount]);

  return (
    <div className="live-count-container">
      <div className="count-display">
        <Users size={32} color="#3b82f6" />
        <div className="count-value">{userCount.toLocaleString()}</div>
        {connectionStatus !== 'connected' && (
          <div className="stale-indicator">Stale data</div>
        )}
      </div>
      
      <div className="sparkline">
        <ResponsiveContainer width="100%" height={80}>
          <LineChart data={history}>
            <XAxis dataKey="time" hide />
            <YAxis hide domain={['auto', 'auto']} />
            <Tooltip 
              labelFormatter={(value) => new Date(value).toLocaleTimeString()}
              formatter={(value) => [`${value} users`, 'Count']}
            />
            <Line 
              type="monotone" 
              dataKey="count" 
              stroke="#3b82f6" 
              strokeWidth={2}
              dot={false}
              isAnimationActive={true}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default LiveUserCount;
EOF

# Message Rate Chart
cat > frontend/src/components/charts/MessageRateChart.jsx << 'EOF'
import React, { useState, useEffect } from 'react';
import { useRealtime } from '../../contexts/RealtimeContext';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

function MessageRateChart() {
  const { messageRate } = useRealtime();
  const [history, setHistory] = useState([]);

  useEffect(() => {
    if (messageRate >= 0) {
      setHistory(prev => {
        const newHistory = [
          ...prev,
          { 
            time: new Date().toLocaleTimeString(), 
            rate: messageRate 
          }
        ];
        // Keep last 30 data points
        return newHistory.slice(-30);
      });
    }
  }, [messageRate]);

  return (
    <div className="chart-container">
      <div className="current-rate">
        <span className="rate-value">{messageRate.toFixed(2)}</span>
        <span className="rate-unit">msg/sec</span>
      </div>
      
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={history} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            dataKey="time" 
            tick={{ fontSize: 12 }}
            interval="preserveStartEnd"
          />
          <YAxis 
            tick={{ fontSize: 12 }}
            label={{ value: 'Messages/sec', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip />
          <Line 
            type="monotone" 
            dataKey="rate" 
            stroke="#8b5cf6" 
            strokeWidth={2}
            dot={false}
            isAnimationActive={true}
            animationDuration={300}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default MessageRateChart;
EOF

# Offline Queue Indicator
cat > frontend/src/components/indicators/OfflineQueueIndicator.jsx << 'EOF'
import React from 'react';
import { useRealtime } from '../../contexts/RealtimeContext';
import { Clock, Activity, Wifi, Server, Zap } from 'lucide-react';

function OfflineQueueIndicator() {
  const { 
    offlineQueue, 
    connectionStatus, 
    latency, 
    lastUpdate,
    userCount,
    messageRate,
    data
  } = useRealtime();

  const formatTime = (timestamp) => {
    if (!timestamp) return 'Never';
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    if (diff < 1000) return 'Just now';
    if (diff < 60000) return `${Math.floor(diff / 1000)}s ago`;
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    return date.toLocaleTimeString();
  };

  const getLatencyColor = (latency) => {
    if (latency < 50) return '#10b981';
    if (latency < 100) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div className="system-status-container">
      <div className="status-grid">
        <div className="status-item">
          <div className="status-item-header">
            <Wifi size={20} color="#3b82f6" />
            <span className="status-item-label">Connection</span>
          </div>
          <div className="status-item-value">
            <span className={`status-badge status-${connectionStatus}`}>
              {connectionStatus.charAt(0).toUpperCase() + connectionStatus.slice(1)}
            </span>
          </div>
        </div>

        <div className="status-item">
          <div className="status-item-header">
            <Activity size={20} color={getLatencyColor(latency)} />
            <span className="status-item-label">Latency</span>
          </div>
          <div className="status-item-value">
            {latency > 0 ? `${Math.round(latency)}ms` : 'N/A'}
          </div>
        </div>

        <div className="status-item">
          <div className="status-item-header">
            <Server size={20} color="#8b5cf6" />
            <span className="status-item-label">Active Users</span>
          </div>
          <div className="status-item-value">{userCount.toLocaleString()}</div>
        </div>

        <div className="status-item">
          <div className="status-item-header">
            <Zap size={20} color="#f59e0b" />
            <span className="status-item-label">Message Rate</span>
          </div>
          <div className="status-item-value">{messageRate.toFixed(2)} msg/s</div>
        </div>
      </div>

      <div className="status-footer">
        <div className="status-meta">
          <Clock size={16} color="#6b7280" />
          <span>Last update: {formatTime(lastUpdate)}</span>
        </div>
        {offlineQueue.length > 0 && (
          <div className="queue-warning">
            <Clock size={16} color="#f59e0b" />
            <span>{offlineQueue.length} queued action{offlineQueue.length !== 1 ? 's' : ''}</span>
          </div>
        )}
      </div>
    </div>
  );
}

export default OfflineQueueIndicator;
EOF

# Auto Refresh Control
cat > frontend/src/components/controls/AutoRefreshControl.jsx << 'EOF'
import React, { useEffect, useRef } from 'react';
import { RefreshCw, Pause } from 'lucide-react';
import axios from 'axios';
import { useRealtime } from '../../contexts/RealtimeContext';

function AutoRefreshControl({ enabled, onToggle }) {
  const { connectionStatus } = useRealtime();
  const intervalRef = useRef(null);

  useEffect(() => {
    if (enabled && connectionStatus === 'offline') {
      // Use polling when WebSocket is offline
      intervalRef.current = setInterval(async () => {
        try {
          const response = await axios.get('/api/stats');
          console.log('Polled stats:', response.data);
        } catch (error) {
          console.error('Polling failed:', error);
        }
      }, 5000);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [enabled, connectionStatus]);

  return (
    <button 
      className={`refresh-control ${enabled ? 'active' : ''}`}
      onClick={() => onToggle(!enabled)}
      title={enabled ? 'Disable auto-refresh' : 'Enable auto-refresh'}
    >
      {enabled ? <RefreshCw size={18} className="spinning" /> : <Pause size={18} />}
      <span>{enabled ? 'Auto-refresh ON' : 'Auto-refresh OFF'}</span>
    </button>
  );
}

export default AutoRefreshControl;
EOF

# Styles
cat > frontend/src/styles/index.css << 'EOF'
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: #f9fafb;
  color: #111827;
}

#root {
  min-height: 100vh;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
EOF

cat > frontend/src/styles/dashboard.css << 'EOF'
.dashboard {
  min-height: 100vh;
  padding: 20px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.dashboard-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: #111827;
}

.header-controls {
  display: flex;
  gap: 15px;
  align-items: center;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.dashboard-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.dashboard-card.full-width {
  grid-column: 1 / -1;
}

.dashboard-card h2 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 20px;
  color: #374151;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.status-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  color: white;
}

.status-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.status-text {
  font-weight: 600;
  font-size: 14px;
  color: #111827;
}

.status-detail {
  font-size: 12px;
  color: #6b7280;
}

.status-update {
  font-size: 11px;
  color: #9ca3af;
}

.reconnect-btn {
  padding: 6px 12px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.reconnect-btn:hover {
  background: #2563eb;
}

.live-count-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.count-display {
  display: flex;
  align-items: center;
  gap: 15px;
}

.count-value {
  font-size: 48px;
  font-weight: 700;
  color: #3b82f6;
}

.stale-indicator {
  padding: 4px 8px;
  background: #fef3c7;
  color: #92400e;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.sparkline {
  width: 100%;
  height: 80px;
}

.chart-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.current-rate {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.rate-value {
  font-size: 36px;
  font-weight: 700;
  color: #8b5cf6;
}

.rate-unit {
  font-size: 14px;
  color: #6b7280;
}

.system-status-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.status-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  transition: all 0.2s;
}

.status-item:hover {
  border-color: #3b82f6;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.1);
}

.status-item-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-item-label {
  font-size: 13px;
  font-weight: 500;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-item-value {
  font-size: 24px;
  font-weight: 700;
  color: #111827;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: capitalize;
}

.status-badge.status-connected {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.status-connecting,
.status-badge.status-reconnecting {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.status-offline {
  background: #fee2e2;
  color: #991b1b;
}

.status-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
}

.status-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #6b7280;
}

.queue-warning {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: #fffbeb;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  color: #92400e;
}

.queue-empty {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px;
  background: #f0fdf4;
  border-radius: 8px;
  color: #166534;
}

.queue-indicator {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 20px;
  background: #fffbeb;
  border-radius: 8px;
}

.queue-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.queue-count {
  font-weight: 600;
  color: #92400e;
}

.queue-status {
  font-size: 14px;
  color: #78350f;
  margin-left: 36px;
}

.refresh-control {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  color: #6b7280;
}

.refresh-control.active {
  background: #eff6ff;
  border-color: #3b82f6;
  color: #3b82f6;
}

.refresh-control:hover {
  border-color: #3b82f6;
}

.offline-banner {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  padding: 16px 24px;
  background: #fef3c7;
  border: 2px solid #f59e0b;
  border-radius: 8px;
  font-weight: 500;
  color: #92400e;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    transform: translateX(-50%) translateY(100px);
    opacity: 0;
  }
  to {
    transform: translateX(-50%) translateY(0);
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  
  .dashboard-header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
  
  .header-controls {
    width: 100%;
    justify-content: space-between;
  }
}
EOF

# ============================================
# TESTS
# ============================================

cat > backend/tests/test_websocket.py << 'EOF'
import pytest
from fastapi.testclient import TestClient
from app.main import app
import json

@pytest.fixture
def client():
    return TestClient(app)

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "connections" in data

def test_stats_endpoint(client):
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert "user_count" in data
    assert "message_rate" in data
    assert "timestamp" in data

def test_websocket_connection(client):
    with client.websocket_connect("/ws") as websocket:
        # Receive connection message
        data = websocket.receive_json()
        assert data["type"] == "connection"
        assert data["data"]["status"] == "connected"

def test_websocket_ping_pong(client):
    with client.websocket_connect("/ws") as websocket:
        # Skip connection message
        websocket.receive_json()
        
        # Send ping
        websocket.send_json({
            "type": "ping",
            "data": {"client_timestamp": 1000}
        })
        
        # Receive pong
        response = websocket.receive_json()
        assert response["type"] == "pong"

def test_websocket_message_ack(client):
    with client.websocket_connect("/ws") as websocket:
        # Skip connection message
        websocket.receive_json()
        
        # Send message
        websocket.send_json({
            "type": "message",
            "data": {"id": "test-123", "content": "Hello"}
        })
        
        # Receive acknowledgment
        response = websocket.receive_json()
        assert response["type"] == "message_ack"
        assert response["data"]["id"] == "test-123"
        assert response["data"]["status"] == "delivered"
EOF

# ============================================
# DOCKER FILES
# ============================================

cat > docker/Dockerfile.backend << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

cat > docker/Dockerfile.frontend << 'EOF'
FROM node:20-alpine as builder

WORKDIR /app

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
EOF

cat > docker/nginx.conf << 'EOF'
server {
    listen 80;
    server_name localhost;
    
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }
    
    location /ws {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
    
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
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
    environment:
      - PYTHONUNBUFFERED=1
    networks:
      - app-network

  frontend:
    build:
      context: .
      dockerfile: docker/Dockerfile.frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
EOF

# ============================================
# BUILD AND RUN SCRIPTS
# ============================================

cat > build.sh << 'EOF'
#!/bin/bash

set -e

echo "=================================="
echo "Building Real-time UI Components"
echo "=================================="

# Check if running with Docker flag
USE_DOCKER=false
if [ "$1" == "--docker" ]; then
    USE_DOCKER=true
fi

if [ "$USE_DOCKER" == "true" ]; then
    echo "Building with Docker..."
    docker-compose build
    docker-compose up -d
    
    echo ""
    echo "Waiting for services to be ready..."
    sleep 10
    
    echo ""
    echo "=================================="
    echo "Services are running!"
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    echo "Health Check: http://localhost:8000/health"
    echo "=================================="
    
    echo ""
    echo "Running tests..."
    docker-compose exec -T backend pytest tests/ -v
    
else
    echo "Building without Docker..."
    
    # Backend setup
    echo "Setting up backend..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    
    # Start backend
    echo "Starting backend..."
    uvicorn app.main:app --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../backend.pid
    
    cd ..
    
    # Frontend setup
    echo "Setting up frontend..."
    cd frontend
    npm install
    
    # Start frontend
    echo "Starting frontend..."
    npm run dev &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../frontend.pid
    
    cd ..
    
    echo ""
    echo "Waiting for services to be ready..."
    sleep 15
    
    echo ""
    echo "=================================="
    echo "Services are running!"
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    echo "Health Check: http://localhost:8000/health"
    echo "=================================="
    
    # Run tests
    echo ""
    echo "Running tests..."
    cd backend
    source venv/bin/activate
    pytest tests/ -v
    cd ..
fi

echo ""
echo "=================================="
echo "Testing API endpoints..."
echo "=================================="
curl -s http://localhost:8000/health | python3 -m json.tool
echo ""
curl -s http://localhost:8000/api/stats | python3 -m json.tool

echo ""
echo "=================================="
echo "Setup complete!"
echo "Open http://localhost:3000 in your browser"
echo "=================================="
echo ""
echo "To stop services, run: ./stop.sh"
EOF

cat > stop.sh << 'EOF'
#!/bin/bash

echo "Stopping services..."

if [ -f "docker-compose.yml" ] && docker-compose ps | grep -q "Up"; then
    echo "Stopping Docker containers..."
    docker-compose down
else
    if [ -f "backend.pid" ]; then
        kill $(cat backend.pid) 2>/dev/null || true
        rm backend.pid
    fi
    
    if [ -f "frontend.pid" ]; then
        kill $(cat frontend.pid) 2>/dev/null || true
        rm frontend.pid
    fi
    
    # Kill any remaining processes
    pkill -f "uvicorn app.main:app" || true
    pkill -f "vite" || true
fi

echo "Services stopped."
EOF

chmod +x build.sh stop.sh

echo ""
echo "=================================="
echo "Project structure created successfully!"
echo "=================================="
echo ""
echo "To build and run:"
echo "  Without Docker: cd $PROJECT_DIR && ./build.sh"
echo "  With Docker:    cd $PROJECT_DIR && ./build.sh --docker"
echo ""
echo "To stop:"
echo "  cd $PROJECT_DIR && ./stop.sh"
echo ""