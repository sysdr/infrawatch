"""Main FastAPI application for security monitoring"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from typing import List
import uvicorn

from collectors.event_collector import EventCollector
from analyzers.threat_analyzer import ThreatAnalyzer
from responders.auto_responder import AutoResponder
from models.database import init_db, get_db, fetchrow_query, fetch_query, execute_query, is_sqlite
from utils.redis_client import get_redis_client

# Global instances
collector = None
analyzer = None
responder = None
active_connections: List[WebSocket] = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global collector, analyzer, responder
    
    # Initialize database
    await init_db()
    
    # Initialize components
    redis = await get_redis_client()
    collector = EventCollector(redis)
    analyzer = ThreatAnalyzer(redis)
    responder = AutoResponder(redis)
    
    # Start background tasks
    asyncio.create_task(collector.start_collection())
    asyncio.create_task(analyzer.start_analysis())
    asyncio.create_task(responder.start_response())
    
    print("Security Monitoring System Started")
    yield
    
    # Cleanup
    await redis.close()
    print("Security Monitoring System Stopped")

app = FastAPI(
    title="Security Monitoring System",
    description="Real-time security event monitoring and threat detection",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "collector": "running",
        "analyzer": "running",
        "responder": "running"
    }

@app.get("/api/events/recent")
async def get_recent_events(limit: int = 100):
    """Get recent security events"""
    use_sqlite = is_sqlite()
    if use_sqlite:
        query = """
            SELECT * FROM security_events 
            ORDER BY timestamp DESC 
            LIMIT ?
        """
    else:
        query = """
            SELECT * FROM security_events 
            ORDER BY timestamp DESC 
            LIMIT $1
        """
    events = await fetch_query(query, limit)
    return events

@app.get("/api/threats/active")
async def get_active_threats():
    """Get active threats"""
    query = """
        SELECT * FROM threats 
        WHERE status = 'active'
        ORDER BY severity DESC, detected_at DESC
    """
    threats = await fetch_query(query)
    return threats

@app.get("/api/analytics/summary")
async def get_analytics_summary():
    """Get security analytics summary"""
    
    use_sqlite = is_sqlite()
    if use_sqlite:
        # SQLite compatible queries
        event_stats = await fetchrow_query("""
            SELECT 
                COUNT(*) as total_events,
                COUNT(CASE WHEN severity >= 60 THEN 1 END) as high_severity,
                COUNT(CASE WHEN datetime(timestamp) > datetime('now', '-1 hour') THEN 1 END) as last_hour
            FROM security_events
            WHERE datetime(timestamp) > datetime('now', '-24 hours')
        """)
        
        threat_stats = await fetchrow_query("""
            SELECT 
                COUNT(*) as total_threats,
                COUNT(CASE WHEN status = 'active' THEN 1 END) as active_threats,
                COUNT(CASE WHEN automated_response = 1 THEN 1 END) as auto_responded
            FROM threats
            WHERE datetime(detected_at) > datetime('now', '-24 hours')
        """)
        
        top_attacks = await fetch_query("""
            SELECT attack_type, COUNT(*) as count
            FROM threats
            WHERE datetime(detected_at) > datetime('now', '-24 hours')
            GROUP BY attack_type
            ORDER BY count DESC
            LIMIT 5
        """)
    else:
        # PostgreSQL queries
        event_stats = await fetchrow_query("""
            SELECT 
                COUNT(*) as total_events,
                COUNT(CASE WHEN severity >= 60 THEN 1 END) as high_severity,
                COUNT(CASE WHEN timestamp > NOW() - INTERVAL '1 hour' THEN 1 END) as last_hour
            FROM security_events
            WHERE timestamp > NOW() - INTERVAL '24 hours'
        """)
        
        threat_stats = await fetchrow_query("""
            SELECT 
                COUNT(*) as total_threats,
                COUNT(CASE WHEN status = 'active' THEN 1 END) as active_threats,
                COUNT(CASE WHEN automated_response THEN 1 END) as auto_responded
            FROM threats
            WHERE detected_at > NOW() - INTERVAL '24 hours'
        """)
        
        top_attacks = await fetch_query("""
            SELECT attack_type, COUNT(*) as count
            FROM threats
            WHERE detected_at > NOW() - INTERVAL '24 hours'
            GROUP BY attack_type
            ORDER BY count DESC
            LIMIT 5
        """)
    
    return {
        "events": event_stats if event_stats else {},
        "threats": threat_stats if threat_stats else {},
        "top_attacks": top_attacks
    }

@app.post("/api/events/simulate")
async def simulate_security_event(event_type: str, count: int = 1):
    """Simulate security events for testing"""
    if count > 100:
        raise HTTPException(400, "Maximum 100 events per request")
    
    events_created = await collector.simulate_events(event_type, count)
    return {"simulated": events_created, "type": event_type}

@app.websocket("/ws/monitoring")
async def websocket_monitoring(websocket: WebSocket):
    """WebSocket for real-time security monitoring"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            # Keep connection alive and listen for client messages
            data = await websocket.receive_text()
            # Client can send preferences/filters if needed
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)

async def broadcast_security_update(data: dict):
    """Broadcast security updates to all connected clients"""
    for connection in active_connections:
        try:
            await connection.send_json(data)
        except:
            active_connections.remove(connection)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
