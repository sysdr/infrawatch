from fastapi import FastAPI, WebSocket, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import uvicorn
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import hashlib
import gzip
import os
import re
from pathlib import Path
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import redis
from pythonjsonlogger import jsonlogger

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/logs")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
LOG_DATA_DIR = Path("../data/logs")
PARSED_DATA_DIR = Path("../data/parsed")
ARCHIVED_DATA_DIR = Path("../data/archived")

# Ensure directories exist
for dir_path in [LOG_DATA_DIR, PARSED_DATA_DIR, ARCHIVED_DATA_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Database setup
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=20, max_overflow=40)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Redis setup
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# Models
class LogEntry(Base):
    __tablename__ = "log_entries"
    
    id = Column(String, primary_key=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    level = Column(String(20), nullable=False, index=True)
    service = Column(String(100), nullable=False, index=True)
    message = Column(Text, nullable=False)
    structured_data = Column(Text)  # JSON
    source_file = Column(String(255))
    trace_id = Column(String(100), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_timestamp_service', 'timestamp', 'service'),
        Index('idx_level_timestamp', 'level', 'timestamp'),
    )

class ParsingRule(Base):
    __tablename__ = "parsing_rules"
    
    id = Column(String, primary_key=True)
    name = Column(String(100), nullable=False)
    pattern = Column(Text, nullable=False)
    format_type = Column(String(50), nullable=False)  # json, apache, syslog, custom
    field_mappings = Column(Text)  # JSON
    priority = Column(Integer, default=100)
    enabled = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

class StorageMetrics(Base):
    __tablename__ = "storage_metrics"
    
    id = Column(String, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    tier = Column(String(20), nullable=False)  # hot, warm, cold
    service = Column(String(100))
    log_count = Column(Integer, default=0)
    storage_bytes = Column(Integer, default=0)

# WebSocket connections manager
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

# Log parser
class LogParser:
    def __init__(self):
        self.rules = []
        self.load_rules()
    
    def load_rules(self):
        """Load parsing rules from database"""
        db = SessionLocal()
        try:
            rules = db.query(ParsingRule).filter(ParsingRule.enabled == 1).order_by(ParsingRule.priority).all()
            self.rules = []
            for rule in rules:
                self.rules.append({
                    'id': rule.id,
                    'name': rule.name,
                    'pattern': rule.pattern,
                    'format_type': rule.format_type,
                    'field_mappings': json.loads(rule.field_mappings) if rule.field_mappings else {}
                })
        finally:
            db.close()
    
    def parse_log_line(self, line: str, source_file: str = "") -> Optional[Dict[str, Any]]:
        """Parse a log line using configured rules"""
        # Try JSON format first
        try:
            data = json.loads(line)
            return self._normalize_json_log(data, source_file)
        except:
            pass
        
        # Try configured patterns
        for rule in self.rules:
            parsed = self._try_pattern(line, rule, source_file)
            if parsed:
                return parsed
        
        # Fallback: create basic structured log
        return self._create_basic_log(line, source_file)
    
    def _normalize_json_log(self, data: dict, source_file: str) -> dict:
        """Normalize JSON log to standard format"""
        return {
            'timestamp': data.get('timestamp', datetime.utcnow().isoformat()),
            'level': data.get('level', data.get('severity', 'INFO')).upper(),
            'service': data.get('service', data.get('app', self._extract_service_from_file(source_file))),
            'message': data.get('message', data.get('msg', str(data))),
            'structured_data': json.dumps(data),
            'source_file': source_file,
            'trace_id': data.get('trace_id', data.get('traceId', ''))
        }
    
    def _try_pattern(self, line: str, rule: dict, source_file: str) -> Optional[dict]:
        """Try to parse line with a specific pattern"""
        try:
            if rule['format_type'] == 'apache':
                return self._parse_apache(line, source_file)
            elif rule['format_type'] == 'syslog':
                return self._parse_syslog(line, source_file)
            elif rule['format_type'] == 'custom':
                return self._parse_custom(line, rule, source_file)
        except:
            pass
        return None
    
    def _parse_apache(self, line: str, source_file: str) -> Optional[dict]:
        """Parse Apache/nginx log format"""
        # Pattern: IP - - [timestamp] "METHOD path HTTP/1.1" status size
        pattern = r'(\S+) \S+ \S+ \[([^\]]+)\] "(\S+) (\S+) \S+" (\d+) (\d+)'
        match = re.match(pattern, line)
        if match:
            ip, timestamp, method, path, status, size = match.groups()
            return {
                'timestamp': timestamp,
                'level': 'INFO' if status.startswith('2') else 'WARN' if status.startswith('4') else 'ERROR',
                'service': self._extract_service_from_file(source_file),
                'message': f"{method} {path} - {status}",
                'structured_data': json.dumps({
                    'ip': ip, 'method': method, 'path': path,
                    'status': int(status), 'size': int(size)
                }),
                'source_file': source_file,
                'trace_id': ''
            }
        return None
    
    def _parse_syslog(self, line: str, source_file: str) -> Optional[dict]:
        """Parse syslog format"""
        # Pattern: <priority>timestamp hostname service[pid]: message
        pattern = r'<(\d+)>(\S+) (\S+) (\S+)\[(\d+)\]: (.+)'
        match = re.match(pattern, line)
        if match:
            priority, timestamp, hostname, service, pid, message = match.groups()
            level = 'ERROR' if int(priority) < 4 else 'WARN' if int(priority) < 6 else 'INFO'
            return {
                'timestamp': timestamp,
                'level': level,
                'service': service,
                'message': message,
                'structured_data': json.dumps({'hostname': hostname, 'pid': pid}),
                'source_file': source_file,
                'trace_id': ''
            }
        return None
    
    def _parse_custom(self, line: str, rule: dict, source_file: str) -> Optional[dict]:
        """Parse using custom regex pattern"""
        match = re.match(rule['pattern'], line)
        if match:
            groups = match.groupdict()
            mappings = rule['field_mappings']
            return {
                'timestamp': groups.get(mappings.get('timestamp', 'timestamp'), datetime.utcnow().isoformat()),
                'level': groups.get(mappings.get('level', 'level'), 'INFO').upper(),
                'service': groups.get(mappings.get('service', 'service'), self._extract_service_from_file(source_file)),
                'message': groups.get(mappings.get('message', 'message'), line),
                'structured_data': json.dumps(groups),
                'source_file': source_file,
                'trace_id': groups.get(mappings.get('trace_id', 'trace_id'), '')
            }
        return None
    
    def _create_basic_log(self, line: str, source_file: str) -> dict:
        """Create basic structured log from unstructured line"""
        # Detect level from keywords
        level = 'INFO'
        line_upper = line.upper()
        if 'ERROR' in line_upper or 'FAIL' in line_upper:
            level = 'ERROR'
        elif 'WARN' in line_upper:
            level = 'WARN'
        elif 'DEBUG' in line_upper:
            level = 'DEBUG'
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'service': self._extract_service_from_file(source_file),
            'message': line,
            'structured_data': json.dumps({'raw': line}),
            'source_file': source_file,
            'trace_id': ''
        }
    
    def _extract_service_from_file(self, file_path: str) -> str:
        """Extract service name from file path"""
        if not file_path:
            return 'unknown'
        # Extract from path like /var/log/api-service/app.log -> api-service
        parts = Path(file_path).parts
        for part in reversed(parts):
            if part not in ['var', 'log', 'logs'] and not part.endswith('.log'):
                return part
        return Path(file_path).stem

parser = LogParser()

# Storage manager
class StorageManager:
    def __init__(self):
        self.hot_age_days = 7
        self.warm_age_days = 90
        self.compression_enabled = True
    
    async def store_log(self, log_data: dict) -> str:
        """Store log entry and return ID"""
        # Generate unique ID
        log_id = hashlib.sha256(
            f"{log_data['timestamp']}{log_data['service']}{log_data['message']}".encode()
        ).hexdigest()[:16]
        
        # Check for duplicate
        if redis_client.exists(f"log:{log_id}"):
            return log_id  # Already processed
        
        # Store in hot storage (PostgreSQL)
        db = SessionLocal()
        try:
            # Parse timestamp
            try:
                timestamp = datetime.fromisoformat(log_data['timestamp'].replace('Z', '+00:00'))
            except:
                timestamp = datetime.utcnow()
            
            entry = LogEntry(
                id=log_id,
                timestamp=timestamp,
                level=log_data['level'],
                service=log_data['service'],
                message=log_data['message'],
                structured_data=log_data.get('structured_data'),
                source_file=log_data.get('source_file', ''),
                trace_id=log_data.get('trace_id', '')
            )
            db.add(entry)
            db.commit()
            
            # Cache for deduplication (expire in 1 hour)
            redis_client.setex(f"log:{log_id}", 3600, "1")
            
            # Update metrics
            redis_client.incr("metrics:logs:total")
            redis_client.incr(f"metrics:logs:service:{log_data['service']}")
            redis_client.incr(f"metrics:logs:level:{log_data['level']}")
            
            return log_id
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    async def rotate_logs(self):
        """Move old logs from hot to warm storage"""
        db = SessionLocal()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.hot_age_days)
            
            # Find old logs
            old_logs = db.query(LogEntry).filter(LogEntry.timestamp < cutoff_date).limit(10000).all()
            
            if old_logs:
                # Group by date and service
                grouped = {}
                for log in old_logs:
                    date_key = log.timestamp.strftime('%Y-%m-%d')
                    service_key = log.service
                    key = f"{date_key}_{service_key}"
                    if key not in grouped:
                        grouped[key] = []
                    grouped[key].append({
                        'id': log.id,
                        'timestamp': log.timestamp.isoformat(),
                        'level': log.level,
                        'service': log.service,
                        'message': log.message,
                        'structured_data': log.structured_data,
                        'source_file': log.source_file,
                        'trace_id': log.trace_id
                    })
                
                # Write to compressed files
                for key, logs in grouped.items():
                    file_path = PARSED_DATA_DIR / f"{key}.json.gz"
                    with gzip.open(file_path, 'wt') as f:
                        for log in logs:
                            f.write(json.dumps(log) + '\n')
                
                # Delete from hot storage
                log_ids = [log.id for log in old_logs]
                db.query(LogEntry).filter(LogEntry.id.in_(log_ids)).delete(synchronize_session=False)
                db.commit()
                
                print(f"Rotated {len(old_logs)} logs to warm storage")
        finally:
            db.close()
    
    async def archive_logs(self):
        """Move old warm logs to cold storage"""
        cutoff_date = datetime.utcnow() - timedelta(days=self.warm_age_days)
        
        # Find old warm files
        for file_path in PARSED_DATA_DIR.glob("*.json.gz"):
            # Extract date from filename
            try:
                date_str = file_path.stem.split('_')[0]
                file_date = datetime.strptime(date_str, '%Y-%m-%d')
                
                if file_date < cutoff_date:
                    # Move to cold storage
                    dest_path = ARCHIVED_DATA_DIR / file_path.name
                    file_path.rename(dest_path)
                    print(f"Archived {file_path.name} to cold storage")
            except:
                continue

storage_manager = StorageManager()

# Background tasks
async def log_rotation_task():
    """Background task for log rotation"""
    while True:
        try:
            await asyncio.sleep(600)  # Run every 10 minutes
            await storage_manager.rotate_logs()
            await storage_manager.archive_logs()
        except Exception as e:
            print(f"Log rotation error: {e}")

async def metrics_aggregation_task():
    """Background task for metrics aggregation"""
    while True:
        try:
            await asyncio.sleep(60)  # Run every minute
            
            # Calculate storage metrics
            db = SessionLocal()
            try:
                # Hot storage
                hot_count = db.query(LogEntry).count()
                
                # Warm storage
                warm_count = 0
                warm_size = 0
                for file_path in PARSED_DATA_DIR.glob("*.json.gz"):
                    warm_size += file_path.stat().st_size
                    # Estimate count (1 line = ~500 bytes compressed)
                    warm_count += warm_size // 500
                
                # Cold storage
                cold_count = 0
                cold_size = 0
                for file_path in ARCHIVED_DATA_DIR.glob("*.json.gz"):
                    cold_size += file_path.stat().st_size
                    cold_count += cold_size // 500
                
                # Update Redis metrics
                redis_client.set("metrics:storage:hot:count", hot_count)
                redis_client.set("metrics:storage:warm:count", warm_count)
                redis_client.set("metrics:storage:warm:bytes", warm_size)
                redis_client.set("metrics:storage:cold:count", cold_count)
                redis_client.set("metrics:storage:cold:bytes", cold_size)
            finally:
                db.close()
        except Exception as e:
            print(f"Metrics aggregation error: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(engine)
    
    # Create default parsing rules
    db = SessionLocal()
    try:
        if db.query(ParsingRule).count() == 0:
            default_rules = [
                ParsingRule(
                    id='json-parser',
                    name='JSON Parser',
                    pattern='',
                    format_type='json',
                    field_mappings=json.dumps({}),
                    priority=1
                ),
                ParsingRule(
                    id='apache-parser',
                    name='Apache/Nginx Parser',
                    pattern='',
                    format_type='apache',
                    field_mappings=json.dumps({}),
                    priority=10
                ),
                ParsingRule(
                    id='syslog-parser',
                    name='Syslog Parser',
                    pattern='',
                    format_type='syslog',
                    field_mappings=json.dumps({}),
                    priority=20
                )
            ]
            for rule in default_rules:
                db.add(rule)
            db.commit()
    finally:
        db.close()
    
    # Start background tasks
    asyncio.create_task(log_rotation_task())
    asyncio.create_task(metrics_aggregation_task())
    
    yield
    
    # Shutdown
    pass

app = FastAPI(title="Log Aggregation System", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Endpoints
@app.post("/api/logs/ingest")
async def ingest_log(log_data: dict, background_tasks: BackgroundTasks):
    """Ingest a single log entry"""
    try:
        # Parse log line if it's raw text
        if 'message' in log_data and isinstance(log_data['message'], str):
            if not log_data.get('level'):
                parsed = parser.parse_log_line(log_data['message'], log_data.get('source_file', ''))
                log_data.update(parsed)
        
        # Store log
        log_id = await storage_manager.store_log(log_data)
        
        # Broadcast to WebSocket clients
        await manager.broadcast({
            'type': 'new_log',
            'data': log_data
        })
        
        return {"success": True, "log_id": log_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/logs/ingest/batch")
async def ingest_logs_batch(logs: List[dict]):
    """Ingest multiple log entries"""
    try:
        results = []
        for log_data in logs:
            if 'message' in log_data and isinstance(log_data['message'], str):
                if not log_data.get('level'):
                    parsed = parser.parse_log_line(log_data['message'], log_data.get('source_file', ''))
                    log_data.update(parsed)
            
            log_id = await storage_manager.store_log(log_data)
            results.append(log_id)
            
            # Broadcast
            await manager.broadcast({
                'type': 'new_log',
                'data': log_data
            })
        
        return {"success": True, "count": len(results), "log_ids": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/logs")
async def get_logs(
    service: Optional[str] = None,
    level: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """Query logs from hot storage"""
    db = SessionLocal()
    try:
        query = db.query(LogEntry)
        
        if service:
            query = query.filter(LogEntry.service == service)
        if level:
            query = query.filter(LogEntry.level == level)
        
        logs = query.order_by(LogEntry.timestamp.desc()).limit(limit).offset(offset).all()
        
        return {
            "logs": [
                {
                    "id": log.id,
                    "timestamp": log.timestamp.isoformat(),
                    "level": log.level,
                    "service": log.service,
                    "message": log.message,
                    "structured_data": json.loads(log.structured_data) if log.structured_data else {},
                    "trace_id": log.trace_id
                }
                for log in logs
            ],
            "total": query.count()
        }
    finally:
        db.close()

@app.get("/api/parsers")
async def get_parsers():
    """Get all parsing rules"""
    db = SessionLocal()
    try:
        rules = db.query(ParsingRule).all()
        return {
            "parsers": [
                {
                    "id": rule.id,
                    "name": rule.name,
                    "format_type": rule.format_type,
                    "pattern": rule.pattern,
                    "field_mappings": json.loads(rule.field_mappings) if rule.field_mappings else {},
                    "priority": rule.priority,
                    "enabled": rule.enabled == 1
                }
                for rule in rules
            ]
        }
    finally:
        db.close()

@app.post("/api/parsers")
async def create_parser(parser_data: dict):
    """Create a new parsing rule"""
    db = SessionLocal()
    try:
        parser_id = parser_data.get('id', hashlib.md5(parser_data['name'].encode()).hexdigest()[:16])
        
        rule = ParsingRule(
            id=parser_id,
            name=parser_data['name'],
            pattern=parser_data.get('pattern', ''),
            format_type=parser_data['format_type'],
            field_mappings=json.dumps(parser_data.get('field_mappings', {})),
            priority=parser_data.get('priority', 100),
            enabled=1 if parser_data.get('enabled', True) else 0
        )
        db.add(rule)
        db.commit()
        
        # Reload parser rules
        parser.load_rules()
        
        return {"success": True, "parser_id": parser_id}
    finally:
        db.close()

@app.get("/api/metrics/summary")
async def get_metrics_summary():
    """Get aggregated metrics"""
    try:
        # Get counts from Redis
        total_logs = int(redis_client.get("metrics:logs:total") or 0)
        
        # Get per-service counts
        services = {}
        for key in redis_client.keys("metrics:logs:service:*"):
            service = key.split(':')[-1]
            count = int(redis_client.get(key) or 0)
            services[service] = count
        
        # Get per-level counts
        levels = {}
        for key in redis_client.keys("metrics:logs:level:*"):
            level = key.split(':')[-1]
            count = int(redis_client.get(key) or 0)
            levels[level] = count
        
        # Get storage metrics
        hot_count = int(redis_client.get("metrics:storage:hot:count") or 0)
        warm_count = int(redis_client.get("metrics:storage:warm:count") or 0)
        warm_bytes = int(redis_client.get("metrics:storage:warm:bytes") or 0)
        cold_count = int(redis_client.get("metrics:storage:cold:count") or 0)
        cold_bytes = int(redis_client.get("metrics:storage:cold:bytes") or 0)
        
        return {
            "total_logs": total_logs,
            "services": services,
            "levels": levels,
            "storage": {
                "hot": {"count": hot_count, "tier": "PostgreSQL"},
                "warm": {"count": warm_count, "bytes": warm_bytes, "tier": "Compressed Files"},
                "cold": {"count": cold_count, "bytes": cold_bytes, "tier": "Archived"}
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    """WebSocket endpoint for real-time log streaming"""
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except:
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
