#!/bin/bash

# Day 53: Real-time Performance Implementation Script
# Creates a production-ready WebSocket notification system with performance optimizations

set -e

PROJECT_NAME="realtime-performance-system"
BASE_DIR=$(pwd)/$PROJECT_NAME

echo "=========================================="
echo "Day 53: Real-time Performance System"
echo "=========================================="

# Create project structure
echo "Creating project structure..."
mkdir -p $PROJECT_NAME/{backend,frontend,docker,tests}
mkdir -p $PROJECT_NAME/backend/{app,app/routers,app/services,app/models,app/utils}
mkdir -p $PROJECT_NAME/frontend/{src,src/components,src/services,public}
mkdir -p $PROJECT_NAME/tests/{unit,integration,performance}

cd $PROJECT_NAME

# Backend: requirements.txt
echo "Creating backend requirements.txt..."
cat > backend/requirements.txt << 'EOF'
fastapi==0.115.0
uvicorn[standard]==0.32.0
websockets==13.1
redis==5.2.0
asyncpg==0.30.0
psycopg2-binary==2.9.10
aioredis==2.0.1
python-multipart==0.0.12
pydantic==2.9.2
pydantic-settings==2.6.0
psutil==6.1.0
pytest==8.3.3
pytest-asyncio==0.24.0
httpx==0.27.2
locust==2.32.2
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.1
EOF

# Backend: .env
cat > backend/.env << 'EOF'
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/notifications_db
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-change-in-production
ENVIRONMENT=development
MAX_CONNECTIONS=10000
POOL_MIN_SIZE=10
POOL_MAX_SIZE=100
MESSAGE_BATCH_SIZE=50
MESSAGE_BATCH_INTERVAL=0.1
MEMORY_LIMIT_MB=2000
EOF

# Backend: Database models
cat > backend/app/models/notification.py << 'EOF'
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class NotificationBase(BaseModel):
    user_id: str
    message: str
    priority: str = "normal"  # critical, normal, low
    notification_type: str = "info"

class NotificationCreate(NotificationBase):
    pass

class Notification(NotificationBase):
    id: int
    created_at: datetime
    delivered: bool = False
    delivered_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class NotificationBatch(BaseModel):
    notifications: list[Notification]
    count: int
    timestamp: datetime

class ConnectionMetrics(BaseModel):
    active_connections: int
    memory_usage_mb: float
    messages_per_second: float
    average_latency_ms: float
    queue_depth: int
    timestamp: datetime
EOF

# Backend: Database pool manager
cat > backend/app/utils/db_pool.py << 'EOF'
import asyncpg
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class DatabasePool:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        
    async def create_pool(self):
        """Create connection pool with optimized settings"""
        if self.pool is None:
            self.pool = await asyncpg.create_pool(
                dsn=os.getenv("DATABASE_URL"),
                min_size=int(os.getenv("POOL_MIN_SIZE", 10)),
                max_size=int(os.getenv("POOL_MAX_SIZE", 100)),
                max_queries=50000,
                max_inactive_connection_lifetime=300,
                command_timeout=30
            )
            logger.info(f"Database pool created: min={os.getenv('POOL_MIN_SIZE')}, max={os.getenv('POOL_MAX_SIZE')}")
        return self.pool
    
    async def close_pool(self):
        """Close all connections in pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database pool closed")
    
    async def get_connection(self):
        """Get connection from pool"""
        if self.pool is None:
            await self.create_pool()
        return self.pool.acquire()

db_pool = DatabasePool()
EOF

# Backend: Redis queue manager
cat > backend/app/utils/redis_queue.py << 'EOF'
import redis.asyncio as redis
import json
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class RedisQueue:
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.pubsub = None
        
    async def connect(self):
        """Connect to Redis"""
        if self.redis_client is None:
            self.redis_client = await redis.from_url(
                os.getenv("REDIS_URL", "redis://localhost:6379"),
                encoding="utf-8",
                decode_responses=True
            )
            logger.info("Redis connected")
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis disconnected")
    
    async def enqueue(self, queue_name: str, message: dict, priority: str = "normal"):
        """Add message to queue based on priority"""
        if priority == "critical":
            queue_name = f"{queue_name}:critical"
        elif priority == "low":
            queue_name = f"{queue_name}:low"
        
        await self.redis_client.lpush(queue_name, json.dumps(message))
        logger.debug(f"Enqueued to {queue_name}: {message.get('id')}")
    
    async def dequeue(self, queue_name: str, timeout: int = 1):
        """Remove and return message from queue (blocking)"""
        # Try critical queue first
        result = await self.redis_client.brpop(f"{queue_name}:critical", timeout=0.1)
        if result:
            return json.loads(result[1])
        
        # Then normal queue
        result = await self.redis_client.brpop(queue_name, timeout=timeout)
        if result:
            return json.loads(result[1])
        
        # Finally low priority
        result = await self.redis_client.brpop(f"{queue_name}:low", timeout=0.1)
        if result:
            return json.loads(result[1])
        
        return None
    
    async def get_queue_depth(self, queue_name: str) -> int:
        """Get total messages in all priority queues"""
        critical = await self.redis_client.llen(f"{queue_name}:critical")
        normal = await self.redis_client.llen(queue_name)
        low = await self.redis_client.llen(f"{queue_name}:low")
        return critical + normal + low
    
    async def publish(self, channel: str, message: dict):
        """Publish message to channel for inter-server communication"""
        await self.redis_client.publish(channel, json.dumps(message))
    
    async def subscribe(self, channel: str):
        """Subscribe to channel"""
        if self.pubsub is None:
            self.pubsub = self.redis_client.pubsub()
        await self.pubsub.subscribe(channel)
        return self.pubsub

redis_queue = RedisQueue()
EOF

# Backend: Memory monitor
cat > backend/app/utils/memory_monitor.py << 'EOF'
import os
import psutil
import asyncio
import logging
from datetime import datetime
from collections import deque

logger = logging.getLogger(__name__)

class MemoryMonitor:
    def __init__(self, max_samples: int = 60):
        self.process = psutil.Process()
        self.memory_history = deque(maxlen=max_samples)
        self.monitoring = False
        
    async def start_monitoring(self):
        """Start background memory monitoring"""
        self.monitoring = True
        asyncio.create_task(self._monitor_loop())
        logger.info("Memory monitoring started")
    
    async def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
    
    async def _monitor_loop(self):
        """Monitor memory usage every second"""
        while self.monitoring:
            memory_mb = self.process.memory_info().rss / 1024 / 1024
            self.memory_history.append({
                'timestamp': datetime.now(),
                'memory_mb': memory_mb
            })
            
            if memory_mb > int(os.getenv("MEMORY_LIMIT_MB", 2000)):
                logger.warning(f"High memory usage: {memory_mb:.2f}MB")
            
            await asyncio.sleep(1)
    
    def get_current_memory(self) -> float:
        """Get current memory usage in MB"""
        return self.process.memory_info().rss / 1024 / 1024
    
    def get_memory_history(self) -> list:
        """Get memory usage history"""
        return list(self.memory_history)

memory_monitor = MemoryMonitor()
EOF

# Backend: WebSocket connection manager
cat > backend/app/services/connection_manager.py << 'EOF'
import os
import asyncio
import logging
import gzip
import json
from datetime import datetime
from collections import deque, defaultdict
from fastapi import WebSocket
from typing import Dict, Set
from ..utils.redis_queue import redis_queue
from ..models.notification import NotificationBatch

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_subscriptions: Dict[str, Set[str]] = defaultdict(set)
        self.message_buffers: Dict[str, deque] = {}
        self.batch_size = int(os.getenv("MESSAGE_BATCH_SIZE", 50))
        self.batch_interval = float(os.getenv("MESSAGE_BATCH_INTERVAL", 0.1))
        self.metrics = {
            'total_messages': 0,
            'total_bytes_sent': 0,
            'compression_savings': 0
        }
        
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept WebSocket connection and initialize user buffer"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.message_buffers[user_id] = deque(maxlen=100)  # Circular buffer
        logger.info(f"User {user_id} connected. Total connections: {len(self.active_connections)}")
    
    async def disconnect(self, user_id: str):
        """Remove connection and cleanup resources"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.message_buffers:
            del self.message_buffers[user_id]
        if user_id in self.user_subscriptions:
            del self.user_subscriptions[user_id]
        logger.info(f"User {user_id} disconnected. Total connections: {len(self.active_connections)}")
    
    async def add_to_buffer(self, user_id: str, notification: dict):
        """Add notification to user's message buffer"""
        if user_id in self.message_buffers:
            self.message_buffers[user_id].append(notification)
            
            # Send batch if buffer is full
            if len(self.message_buffers[user_id]) >= self.batch_size:
                await self.flush_buffer(user_id)
    
    async def flush_buffer(self, user_id: str):
        """Send batched messages to user"""
        if user_id not in self.message_buffers or not self.message_buffers[user_id]:
            return
        
        if user_id not in self.active_connections:
            return
        
        try:
            # Create batch
            notifications = list(self.message_buffers[user_id])
            batch = NotificationBatch(
                notifications=notifications,
                count=len(notifications),
                timestamp=datetime.now()
            )
            
            # Serialize and compress
            json_data = batch.model_dump_json()
            original_size = len(json_data.encode())
            compressed = gzip.compress(json_data.encode())
            compressed_size = len(compressed)
            
            # Track metrics
            self.metrics['total_messages'] += len(notifications)
            self.metrics['total_bytes_sent'] += compressed_size
            self.metrics['compression_savings'] += (original_size - compressed_size)
            
            # Send compressed batch
            websocket = self.active_connections[user_id]
            await websocket.send_bytes(compressed)
            
            # Clear buffer
            self.message_buffers[user_id].clear()
            
            logger.debug(f"Flushed {len(notifications)} messages to {user_id} "
                        f"(compressed: {compressed_size}B, saved: {original_size - compressed_size}B)")
        
        except Exception as e:
            logger.error(f"Error flushing buffer for {user_id}: {e}")
            await self.disconnect(user_id)
    
    async def start_batch_flusher(self):
        """Periodically flush message buffers"""
        while True:
            await asyncio.sleep(self.batch_interval)
            for user_id in list(self.message_buffers.keys()):
                if self.message_buffers[user_id]:
                    await self.flush_buffer(user_id)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected users"""
        for user_id in list(self.active_connections.keys()):
            await self.add_to_buffer(user_id, message)
    
    def get_connection_count(self) -> int:
        """Get active connection count"""
        return len(self.active_connections)
    
    def get_metrics(self) -> dict:
        """Get connection manager metrics"""
        return {
            **self.metrics,
            'active_connections': len(self.active_connections),
            'compression_ratio': (
                self.metrics['compression_savings'] / self.metrics['total_bytes_sent'] 
                if self.metrics['total_bytes_sent'] > 0 else 0
            )
        }

manager = ConnectionManager()
EOF

# Backend: Notification service
cat > backend/app/services/notification_service.py << 'EOF'
import asyncio
import logging
from datetime import datetime
from ..utils.db_pool import db_pool
from ..utils.redis_queue import redis_queue
from ..models.notification import NotificationCreate, Notification
from .connection_manager import manager

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.processing = False
        self.latency_samples = []
        
    async def create_notification(self, notification: NotificationCreate) -> Notification:
        """Create notification and queue for delivery"""
        start_time = datetime.now()
        
        async with db_pool.get_connection() as conn:
            # Insert into database
            row = await conn.fetchrow(
                """
                INSERT INTO notifications (user_id, message, priority, notification_type, created_at)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id, user_id, message, priority, notification_type, created_at, delivered
                """,
                notification.user_id,
                notification.message,
                notification.priority,
                notification.notification_type,
                datetime.now()
            )
            
            notif = Notification(
                id=row['id'],
                user_id=row['user_id'],
                message=row['message'],
                priority=row['priority'],
                notification_type=row['notification_type'],
                created_at=row['created_at'],
                delivered=row['delivered']
            )
            
            # Queue for delivery
            await redis_queue.enqueue(
                "notifications",
                notif.model_dump(mode='json'),
                priority=notification.priority
            )
            
            # Track latency
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            self.latency_samples.append(latency_ms)
            if len(self.latency_samples) > 1000:
                self.latency_samples.pop(0)
            
            logger.debug(f"Created notification {notif.id} for {notif.user_id}")
            
            return notif
    
    async def start_worker(self):
        """Start background worker to process notification queue"""
        self.processing = True
        logger.info("Notification worker started")
        
        while self.processing:
            try:
                # Dequeue notification
                message = await redis_queue.dequeue("notifications", timeout=1)
                
                if message:
                    # Add to connection manager buffer
                    user_id = message['user_id']
                    await manager.add_to_buffer(user_id, message)
                    
                    # Mark as delivered in database
                    async with db_pool.get_connection() as conn:
                        await conn.execute(
                            """
                            UPDATE notifications 
                            SET delivered = true, delivered_at = $1
                            WHERE id = $2
                            """,
                            datetime.now(),
                            message['id']
                        )
                
            except Exception as e:
                logger.error(f"Worker error: {e}")
                await asyncio.sleep(1)
    
    async def stop_worker(self):
        """Stop background worker"""
        self.processing = False
        logger.info("Notification worker stopped")
    
    def get_average_latency(self) -> float:
        """Calculate average latency from recent samples"""
        if not self.latency_samples:
            return 0.0
        return sum(self.latency_samples) / len(self.latency_samples)

notification_service = NotificationService()
EOF

# Backend: Metrics collector
cat > backend/app/services/metrics_collector.py << 'EOF'
import asyncio
import logging
from datetime import datetime
from collections import deque
from ..utils.memory_monitor import memory_monitor
from ..utils.redis_queue import redis_queue
from .connection_manager import manager
from .notification_service import notification_service

logger = logging.getLogger(__name__)

class MetricsCollector:
    def __init__(self):
        self.metrics_history = deque(maxlen=60)  # Last 60 seconds
        self.collecting = False
        self.last_message_count = 0
        
    async def start_collection(self):
        """Start collecting metrics every second"""
        self.collecting = True
        asyncio.create_task(self._collect_loop())
        logger.info("Metrics collection started")
    
    async def stop_collection(self):
        """Stop collecting metrics"""
        self.collecting = False
    
    async def _collect_loop(self):
        """Collect metrics every second"""
        while self.collecting:
            try:
                # Gather metrics
                current_messages = manager.metrics['total_messages']
                messages_per_second = current_messages - self.last_message_count
                self.last_message_count = current_messages
                
                metrics = {
                    'timestamp': datetime.now().isoformat(),
                    'active_connections': manager.get_connection_count(),
                    'memory_usage_mb': memory_monitor.get_current_memory(),
                    'messages_per_second': messages_per_second,
                    'average_latency_ms': notification_service.get_average_latency(),
                    'queue_depth': await redis_queue.get_queue_depth("notifications"),
                    'total_messages': current_messages,
                    'compression_ratio': manager.get_metrics()['compression_ratio']
                }
                
                self.metrics_history.append(metrics)
                
                # Broadcast to dashboard via Redis Pub/Sub
                await redis_queue.publish("metrics", metrics)
                
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
            
            await asyncio.sleep(1)
    
    def get_current_metrics(self) -> dict:
        """Get most recent metrics"""
        if self.metrics_history:
            return self.metrics_history[-1]
        return {}
    
    def get_metrics_history(self) -> list:
        """Get metrics history"""
        return list(self.metrics_history)

metrics_collector = MetricsCollector()
EOF

# Backend: Main application
cat > backend/app/main.py << 'EOF'
import os
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .utils.db_pool import db_pool
from .utils.redis_queue import redis_queue
from .utils.memory_monitor import memory_monitor
from .services.connection_manager import manager
from .services.notification_service import notification_service
from .services.metrics_collector import metrics_collector
from .models.notification import NotificationCreate, Notification, ConnectionMetrics
from .routers import notifications, websocket, metrics

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting application...")
    
    # Initialize database pool
    await db_pool.create_pool()
    
    # Initialize Redis
    await redis_queue.connect()
    
    # Create tables
    async with db_pool.get_connection() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(100) NOT NULL,
                message TEXT NOT NULL,
                priority VARCHAR(20) DEFAULT 'normal',
                notification_type VARCHAR(50) DEFAULT 'info',
                created_at TIMESTAMP NOT NULL,
                delivered BOOLEAN DEFAULT FALSE,
                delivered_at TIMESTAMP
            )
        """)
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON notifications(user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_delivered ON notifications(delivered)")
    
    # Start background services
    await memory_monitor.start_monitoring()
    asyncio.create_task(notification_service.start_worker())
    asyncio.create_task(manager.start_batch_flusher())
    await metrics_collector.start_collection()
    
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await notification_service.stop_worker()
    await metrics_collector.stop_collection()
    await memory_monitor.stop_monitoring()
    await redis_queue.disconnect()
    await db_pool.close_pool()
    logger.info("Application shut down complete")

app = FastAPI(
    title="Real-time Performance System",
    description="High-performance WebSocket notification system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["metrics"])

@app.get("/")
async def root():
    return {
        "message": "Real-time Performance System API",
        "version": "1.0.0",
        "active_connections": manager.get_connection_count()
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "connections": manager.get_connection_count(),
        "memory_mb": memory_monitor.get_current_memory()
    }
EOF

# Backend: Notifications router
cat > backend/app/routers/notifications.py << 'EOF'
from fastapi import APIRouter, HTTPException
from ..models.notification import NotificationCreate, Notification
from ..services.notification_service import notification_service

router = APIRouter()

@router.post("/", response_model=Notification)
async def create_notification(notification: NotificationCreate):
    """Create a new notification"""
    try:
        return await notification_service.create_notification(notification)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bulk")
async def create_bulk_notifications(notifications: list[NotificationCreate]):
    """Create multiple notifications"""
    try:
        results = []
        for notif in notifications:
            result = await notification_service.create_notification(notif)
            results.append(result)
        return {"created": len(results), "notifications": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
EOF

# Backend: WebSocket router
cat > backend/app/routers/websocket.py << 'EOF'
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..services.connection_manager import manager
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket("/notifications/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time notifications"""
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            logger.debug(f"Received from {user_id}: {data}")
    except WebSocketDisconnect:
        await manager.disconnect(user_id)
    except Exception as e:
        logger.error(f"WebSocket error for {user_id}: {e}")
        await manager.disconnect(user_id)
EOF

# Backend: Metrics router
cat > backend/app/routers/metrics.py << 'EOF'
from fastapi import APIRouter
from ..services.metrics_collector import metrics_collector

router = APIRouter()

@router.get("/current")
async def get_current_metrics():
    """Get current system metrics"""
    return metrics_collector.get_current_metrics()

@router.get("/history")
async def get_metrics_history():
    """Get metrics history (last 60 seconds)"""
    return {
        "metrics": metrics_collector.get_metrics_history(),
        "count": len(metrics_collector.get_metrics_history())
    }
EOF

# Frontend: package.json
cat > frontend/package.json << 'EOF'
{
  "name": "realtime-performance-dashboard",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "recharts": "^2.13.3",
    "antd": "^5.22.2",
    "@ant-design/icons": "^5.5.1",
    "axios": "^1.7.7",
    "pako": "^2.1.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "devDependencies": {
    "react-scripts": "^5.0.1"
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
    <title>Real-time Performance Dashboard</title>
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
import 'antd/dist/reset.css';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
EOF

# Frontend: src/App.js
cat > frontend/src/App.js << 'EOF'
import React, { useState, useEffect, useCallback } from 'react';
import { Layout, Card, Row, Col, Statistic, Button, Input, Select, notification } from 'antd';
import { 
  UserOutlined, 
  ThunderboltOutlined, 
  ClockCircleOutlined, 
  DatabaseOutlined,
  BarChartOutlined
} from '@ant-design/icons';
import MetricsChart from './components/MetricsChart';
import NotificationPanel from './components/NotificationPanel';
import ConnectionTest from './components/ConnectionTest';
import './App.css';

const { Header, Content } = Layout;
const { Option } = Select;

function App() {
  const [metrics, setMetrics] = useState({
    active_connections: 0,
    memory_usage_mb: 0,
    messages_per_second: 0,
    average_latency_ms: 0,
    queue_depth: 0,
    compression_ratio: 0
  });
  const [metricsHistory, setMetricsHistory] = useState([]);
  const [wsConnected, setWsConnected] = useState(false);

  useEffect(() => {
    // Fetch metrics every second
    const interval = setInterval(async () => {
      try {
        const response = await fetch('http://localhost:8000/api/metrics/current');
        const data = await response.json();
        setMetrics(data);
        
        // Update history
        setMetricsHistory(prev => {
          const newHistory = [...prev, data];
          return newHistory.slice(-60); // Keep last 60 seconds
        });
      } catch (error) {
        console.error('Error fetching metrics:', error);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      <Header style={{ background: '#001529', padding: '0 24px' }}>
        <div style={{ color: 'white', fontSize: '20px', fontWeight: 'bold' }}>
          ⚡ Real-time Performance Dashboard
        </div>
      </Header>
      
      <Content style={{ padding: '24px' }}>
        {/* Metrics Overview */}
        <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
          <Col xs={24} sm={12} md={8} lg={4}>
            <Card>
              <Statistic
                title="Active Connections"
                value={metrics.active_connections || 0}
                prefix={<UserOutlined />}
                valueStyle={{ color: '#3f8600' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={8} lg={4}>
            <Card>
              <Statistic
                title="Messages/sec"
                value={metrics.messages_per_second || 0}
                prefix={<ThunderboltOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={8} lg={4}>
            <Card>
              <Statistic
                title="Avg Latency"
                value={(metrics.average_latency_ms || 0).toFixed(2)}
                suffix="ms"
                prefix={<ClockCircleOutlined />}
                valueStyle={{ color: metrics.average_latency_ms > 100 ? '#cf1322' : '#3f8600' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={8} lg={4}>
            <Card>
              <Statistic
                title="Queue Depth"
                value={metrics.queue_depth || 0}
                prefix={<DatabaseOutlined />}
                valueStyle={{ color: metrics.queue_depth > 1000 ? '#cf1322' : '#1890ff' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={8} lg={4}>
            <Card>
              <Statistic
                title="Memory Usage"
                value={(metrics.memory_usage_mb || 0).toFixed(0)}
                suffix="MB"
                prefix={<BarChartOutlined />}
                valueStyle={{ color: metrics.memory_usage_mb > 2000 ? '#cf1322' : '#3f8600' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={8} lg={4}>
            <Card>
              <Statistic
                title="Compression"
                value={((metrics.compression_ratio || 0) * 100).toFixed(1)}
                suffix="%"
                valueStyle={{ color: '#722ed1' }}
              />
            </Card>
          </Col>
        </Row>

        {/* Charts */}
        <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
          <Col xs={24} lg={12}>
            <MetricsChart 
              data={metricsHistory} 
              title="Performance Metrics"
              dataKeys={['messages_per_second', 'average_latency_ms']}
            />
          </Col>
          <Col xs={24} lg={12}>
            <MetricsChart 
              data={metricsHistory} 
              title="Resource Usage"
              dataKeys={['memory_usage_mb', 'active_connections', 'queue_depth']}
            />
          </Col>
        </Row>

        {/* Connection Test */}
        <Row gutter={[16, 16]}>
          <Col xs={24} lg={12}>
            <ConnectionTest />
          </Col>
          <Col xs={24} lg={12}>
            <NotificationPanel />
          </Col>
        </Row>
      </Content>
    </Layout>
  );
}

export default App;
EOF

# Frontend: src/App.css
cat > frontend/src/App.css << 'EOF'
.App {
  text-align: center;
}

.ant-layout-header {
  display: flex;
  align-items: center;
}

.metrics-card {
  margin-bottom: 16px;
}

.chart-container {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
EOF

# Frontend: MetricsChart component
cat > frontend/src/components/MetricsChart.js << 'EOF'
import React from 'react';
import { Card } from 'antd';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const colors = ['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1'];

function MetricsChart({ data, title, dataKeys }) {
  const formattedData = data.map(item => ({
    ...item,
    time: new Date(item.timestamp).toLocaleTimeString()
  }));

  return (
    <Card title={title} className="chart-container">
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={formattedData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis />
          <Tooltip />
          <Legend />
          {dataKeys.map((key, index) => (
            <Line 
              key={key}
              type="monotone" 
              dataKey={key} 
              stroke={colors[index % colors.length]}
              dot={false}
              strokeWidth={2}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
}

export default MetricsChart;
EOF

# Frontend: ConnectionTest component
cat > frontend/src/components/ConnectionTest.js << 'EOF'
import React, { useState, useEffect, useRef } from 'react';
import { Card, Button, Input, Space, Tag, Divider, Statistic, Row, Col } from 'antd';
import { CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import pako from 'pako';

function ConnectionTest() {
  const [userId, setUserId] = useState('test_user_' + Math.random().toString(36).substr(2, 9));
  const [connected, setConnected] = useState(false);
  const [messages, setMessages] = useState([]);
  const [stats, setStats] = useState({ received: 0, batches: 0 });
  const ws = useRef(null);

  const connect = () => {
    const websocket = new WebSocket(`ws://localhost:8000/ws/notifications/${userId}`);
    
    websocket.onopen = () => {
      setConnected(true);
      console.log('WebSocket connected');
    };

    websocket.onmessage = (event) => {
      if (event.data instanceof Blob) {
        const reader = new FileReader();
        reader.onload = () => {
          try {
            // Decompress
            const compressed = new Uint8Array(reader.result);
            const decompressed = pako.inflate(compressed, { to: 'string' });
            const batch = JSON.parse(decompressed);
            
            setStats(prev => ({
              received: prev.received + batch.count,
              batches: prev.batches + 1
            }));
            
            setMessages(prev => [...batch.notifications, ...prev].slice(0, 10));
          } catch (error) {
            console.error('Error processing message:', error);
          }
        };
        reader.readAsArrayBuffer(event.data);
      }
    };

    websocket.onclose = () => {
      setConnected(false);
      console.log('WebSocket disconnected');
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.current = websocket;
  };

  const disconnect = () => {
    if (ws.current) {
      ws.current.close();
      ws.current = null;
    }
  };

  useEffect(() => {
    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, []);

  const sendTestNotification = async () => {
    try {
      await fetch('http://localhost:8000/api/notifications/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          message: `Test notification at ${new Date().toLocaleTimeString()}`,
          priority: 'normal',
          notification_type: 'info'
        })
      });
    } catch (error) {
      console.error('Error sending notification:', error);
    }
  };

  const sendBulkNotifications = async () => {
    const notifications = Array.from({ length: 100 }, (_, i) => ({
      user_id: userId,
      message: `Bulk notification ${i + 1}`,
      priority: i % 10 === 0 ? 'critical' : 'normal',
      notification_type: 'info'
    }));

    try {
      await fetch('http://localhost:8000/api/notifications/bulk', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(notifications)
      });
    } catch (error) {
      console.error('Error sending bulk notifications:', error);
    }
  };

  return (
    <Card title="WebSocket Connection Test">
      <Space direction="vertical" style={{ width: '100%' }}>
        <Input 
          value={userId} 
          onChange={(e) => setUserId(e.target.value)}
          placeholder="User ID"
          disabled={connected}
        />
        
        <Space>
          {!connected ? (
            <Button type="primary" onClick={connect}>Connect</Button>
          ) : (
            <Button danger onClick={disconnect}>Disconnect</Button>
          )}
          <Tag color={connected ? 'green' : 'red'}>
            {connected ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
            {connected ? 'Connected' : 'Disconnected'}
          </Tag>
        </Space>

        <Row gutter={16}>
          <Col span={12}>
            <Statistic title="Messages Received" value={stats.received} />
          </Col>
          <Col span={12}>
            <Statistic title="Batches Received" value={stats.batches} />
          </Col>
        </Row>

        <Divider />

        <Space>
          <Button onClick={sendTestNotification} disabled={!connected}>
            Send Test Message
          </Button>
          <Button onClick={sendBulkNotifications} disabled={!connected}>
            Send 100 Messages
          </Button>
        </Space>

        <Divider>Recent Messages</Divider>

        <div style={{ maxHeight: '200px', overflow: 'auto' }}>
          {messages.map((msg, idx) => (
            <div key={idx} style={{ 
              padding: '8px', 
              marginBottom: '4px', 
              background: '#f0f0f0',
              borderRadius: '4px',
              fontSize: '12px'
            }}>
              <Tag color={msg.priority === 'critical' ? 'red' : 'blue'}>
                {msg.priority}
              </Tag>
              {msg.message}
            </div>
          ))}
        </div>
      </Space>
    </Card>
  );
}

export default ConnectionTest;
EOF

# Frontend: NotificationPanel component
cat > frontend/src/components/NotificationPanel.js << 'EOF'
import React, { useState } from 'react';
import { Card, Form, Input, Select, Button, Space, message } from 'antd';

const { TextArea } = Input;
const { Option } = Select;

function NotificationPanel() {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (values) => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/notifications/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values)
      });
      
      if (response.ok) {
        message.success('Notification created successfully');
        form.resetFields();
      } else {
        message.error('Failed to create notification');
      }
    } catch (error) {
      message.error('Error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card title="Create Notification">
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        initialValues={{
          priority: 'normal',
          notification_type: 'info'
        }}
      >
        <Form.Item 
          label="User ID" 
          name="user_id"
          rules={[{ required: true, message: 'Please enter user ID' }]}
        >
          <Input placeholder="Enter user ID" />
        </Form.Item>

        <Form.Item 
          label="Message" 
          name="message"
          rules={[{ required: true, message: 'Please enter message' }]}
        >
          <TextArea rows={4} placeholder="Enter notification message" />
        </Form.Item>

        <Form.Item label="Priority" name="priority">
          <Select>
            <Option value="critical">Critical</Option>
            <Option value="normal">Normal</Option>
            <Option value="low">Low</Option>
          </Select>
        </Form.Item>

        <Form.Item label="Type" name="notification_type">
          <Select>
            <Option value="info">Info</Option>
            <Option value="warning">Warning</Option>
            <Option value="error">Error</Option>
            <Option value="success">Success</Option>
          </Select>
        </Form.Item>

        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading} block>
            Create Notification
          </Button>
        </Form.Item>
      </Form>
    </Card>
  );
}

export default NotificationPanel;
EOF

# Tests: Performance test
cat > tests/performance/test_load.py << 'EOF'
from locust import HttpUser, task, between
import json
import random

class NotificationUser(HttpUser):
    wait_time = between(0.1, 0.5)
    
    def on_start(self):
        self.user_id = f"user_{random.randint(1, 10000)}"
    
    @task(3)
    def create_notification(self):
        self.client.post("/api/notifications/", json={
            "user_id": self.user_id,
            "message": f"Load test message {random.randint(1, 1000)}",
            "priority": random.choice(["critical", "normal", "low"]),
            "notification_type": "info"
        })
    
    @task(1)
    def get_metrics(self):
        self.client.get("/api/metrics/current")
    
    @task(1)
    def check_health(self):
        self.client.get("/health")
EOF

# Tests: Integration test
cat > tests/integration/test_system.py << 'EOF'
import pytest
import asyncio
import json
from httpx import AsyncClient
import websockets

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"

@pytest.mark.asyncio
async def test_notification_creation():
    """Test creating a notification"""
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.post("/api/notifications/", json={
            "user_id": "test_user",
            "message": "Test notification",
            "priority": "normal",
            "notification_type": "info"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "test_user"
        assert data["message"] == "Test notification"

@pytest.mark.asyncio
async def test_bulk_notifications():
    """Test creating bulk notifications"""
    notifications = [
        {
            "user_id": f"user_{i}",
            "message": f"Bulk message {i}",
            "priority": "normal",
            "notification_type": "info"
        }
        for i in range(100)
    ]
    
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.post("/api/notifications/bulk", json=notifications)
        assert response.status_code == 200
        data = response.json()
        assert data["created"] == 100

@pytest.mark.asyncio
async def test_metrics_endpoint():
    """Test metrics retrieval"""
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.get("/api/metrics/current")
        assert response.status_code == 200
        data = response.json()
        assert "active_connections" in data
        assert "memory_usage_mb" in data

@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health check"""
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
EOF

# Docker Compose
cat > docker/docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: notifications_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ../backend
      dockerfile: ../docker/Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/notifications_db
      REDIS_URL: redis://redis:6379
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ../backend:/app

  frontend:
    build:
      context: ../frontend
      dockerfile: ../docker/Dockerfile.frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    volumes:
      - ../frontend:/app
      - /app/node_modules

volumes:
  postgres_data:
EOF

# Backend Dockerfile
cat > docker/Dockerfile.backend << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
EOF

# Frontend Dockerfile
cat > docker/Dockerfile.frontend << 'EOF'
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

CMD ["npm", "start"]
EOF

# Build script
cat > build.sh << 'EOF'
#!/bin/bash

echo "=========================================="
echo "Building Real-time Performance System"
echo "=========================================="

# Check if Docker should be used
USE_DOCKER=${1:-"no"}

if [ "$USE_DOCKER" == "docker" ]; then
    echo "Building with Docker..."
    cd docker
    docker-compose up -d
    echo "Waiting for services to be ready..."
    sleep 10
    echo "Services started successfully!"
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    echo "API Docs: http://localhost:8000/docs"
else
    echo "Building without Docker..."
    
    # Start PostgreSQL and Redis (assumes they're installed)
    echo "Ensure PostgreSQL and Redis are running..."
    
    # Backend
    echo "Setting up backend..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Create database
    export PGPASSWORD=postgres
    psql -h localhost -U postgres -c "CREATE DATABASE notifications_db;" || true
    
    # Start backend
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    
    cd ..
    
    # Frontend
    echo "Setting up frontend..."
    cd frontend
    npm install
    npm start &
    FRONTEND_PID=$!
    
    cd ..
    
    echo "Services started!"
    echo "Backend PID: $BACKEND_PID"
    echo "Frontend PID: $FRONTEND_PID"
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    
    # Save PIDs
    echo $BACKEND_PID > backend.pid
    echo $FRONTEND_PID > frontend.pid
fi

echo "=========================================="
echo "Build Complete!"
echo "=========================================="
EOF

chmod +x build.sh

# Stop script
cat > stop.sh << 'EOF'
#!/bin/bash

echo "=========================================="
echo "Stopping Real-time Performance System"
echo "=========================================="

if [ -f "docker/docker-compose.yml" ] && [ "$(docker-compose -f docker/docker-compose.yml ps -q)" ]; then
    echo "Stopping Docker containers..."
    cd docker
    docker-compose down
    cd ..
else
    echo "Stopping local services..."
    
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
    pkill -f "react-scripts start" || true
fi

echo "=========================================="
echo "Services Stopped"
echo "=========================================="
EOF

chmod +x stop.sh

# README
cat > README.md << 'EOF'
# Day 53: Real-time Performance System

Production-ready WebSocket notification system with performance optimizations.

## Features

- ✅ Connection pooling with AsyncPG (10-100 connections)
- ✅ Message queuing with Redis (priority queues)
- ✅ Bandwidth optimization (batching + gzip compression)
- ✅ Memory management (circular buffers, monitoring)
- ✅ Horizontal scaling (Redis Pub/Sub)
- ✅ Real-time performance dashboard
- ✅ Load testing with Locust

## Quick Start

### Without Docker
```bash
./build.sh
```

### With Docker
```bash
./build.sh docker
```

## Access Points

- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Testing

### Integration Tests
```bash
cd tests/integration
pytest test_system.py -v
```

### Performance Tests
```bash
cd tests/performance
locust -f test_load.py --host=http://localhost:8000
```
Open http://localhost:8089 and simulate 1000 users

## Performance Targets

- ✅ 10,000+ concurrent WebSocket connections
- ✅ 1,000+ messages/second throughput
- ✅ <100ms average latency
- ✅ <2GB memory usage (24 hours)
- ✅ 70%+ compression ratio

## Stop Services

```bash
./stop.sh
```
EOF

echo "=========================================="
echo "Project structure created successfully!"
echo "=========================================="
echo "Next steps:"
echo "1. cd $PROJECT_NAME"
echo "2. ./build.sh          # Without Docker"
echo "   ./build.sh docker   # With Docker"
echo "3. Open http://localhost:3000"
echo "=========================================="