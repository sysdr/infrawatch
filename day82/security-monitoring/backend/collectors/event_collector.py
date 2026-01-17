"""Security Event Collection System"""
import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, List
import random
import hashlib
from redis import asyncio as aioredis

from models.database import get_db, execute_query, _use_sqlite
from utils.geo_enrichment import enrich_with_geo

class EventCollector:
    """Collects and processes security events from multiple sources"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.stream_name = "security:events:stream"
        self.processed_count = 0
        
    async def start_collection(self):
        """Start continuous event collection"""
        print("Event Collector started")
        
        while True:
            try:
                # Read from Redis stream
                streams = await self.redis.xread(
                    {self.stream_name: '$'}, 
                    block=1000,
                    count=100
                )
                
                for stream_name, messages in streams:
                    for message_id, data in messages:
                        await self.process_event(data)
                        
            except Exception as e:
                print(f"Collection error: {e}")
                await asyncio.sleep(1)
    
    async def process_event(self, raw_event: Dict):
        """Process and enrich security event"""
        try:
            # Helper to safely get and decode values
            def get_value(key, default=''):
                val = raw_event.get(key.encode() if isinstance(key, str) else key, None)
                if val is None:
                    # Try bytes key
                    val = raw_event.get(key if isinstance(key, bytes) else key.encode(), None)
                if val is None:
                    return default
                if isinstance(val, bytes):
                    return val.decode()
                return val
            
            # Normalize event data
            event_id = get_value('event_id')
            if not event_id:
                # Generate event_id if missing
                event_id = hashlib.sha256(
                    f"{get_value('user_id', 'anonymous')}_{get_value('action')}_{datetime.now().isoformat()}".encode()
                ).hexdigest()[:16]
            
            # Parse metadata safely
            metadata_str = get_value('metadata', '{}')
            try:
                metadata = json.loads(metadata_str) if metadata_str else {}
            except (json.JSONDecodeError, ValueError):
                # If it's not valid JSON, try eval as fallback (for old format)
                try:
                    metadata = eval(metadata_str) if metadata_str else {}
                except:
                    metadata = {}
            
            event = {
                'event_id': event_id,
                'event_type': get_value('event_type'),
                'user_id': get_value('user_id'),
                'ip_address': get_value('ip_address'),
                'user_agent': get_value('user_agent'),
                'action': get_value('action'),
                'resource': get_value('resource'),
                'success': get_value('success', 'true').lower() == 'true',
                'timestamp': get_value('timestamp') or datetime.now(timezone.utc).isoformat(),
                'metadata': metadata
            }
            
            # Enrich with geolocation
            event = await enrich_with_geo(event)
            
            # Store in database
            await self.store_event(event)
            
            # Publish for analysis
            await self.redis.publish('security:events:analysis', json.dumps(event))
            
            self.processed_count += 1
            
        except Exception as e:
            print(f"Event processing error: {e}")
    
    async def store_event(self, event: Dict):
        """Store event in database"""
        if _use_sqlite:
            # SQLite uses ? placeholders
            query = """
                INSERT INTO security_events (
                    event_id, event_type, user_id, ip_address, user_agent,
                    action, resource, success, timestamp, country, city,
                    latitude, longitude, metadata, severity
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
        else:
            # PostgreSQL uses $1, $2, etc.
            query = """
                INSERT INTO security_events (
                    event_id, event_type, user_id, ip_address, user_agent,
                    action, resource, success, timestamp, country, city,
                    latitude, longitude, metadata, severity
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
            """
        
        # Use execute_query helper that handles both SQLite and PostgreSQL
        await execute_query(
            query,
            event['event_id'],
            event['event_type'],
            event.get('user_id'),
            event['ip_address'],
            event.get('user_agent'),
            event['action'],
            event.get('resource'),
            1 if event['success'] else 0 if _use_sqlite else event['success'],  # SQLite uses integer for boolean
            event['timestamp'],
            event.get('country'),
            event.get('city'),
            event.get('latitude'),
            event.get('longitude'),
            json.dumps(event.get('metadata', {})),
            0  # Initial severity, will be updated by analyzer
        )
    
    async def ingest_event(self, event: Dict) -> str:
        """Ingest a new security event"""
        event_id = hashlib.sha256(
            f"{event.get('user_id', 'anonymous')}_{event.get('action')}_{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        event['event_id'] = event_id
        
        # Convert event to string values for Redis stream
        # Ensure metadata is JSON string
        event_data = {}
        for k, v in event.items():
            if v is None:
                continue
            if k == 'metadata':
                event_data[k] = json.dumps(v) if isinstance(v, dict) else str(v)
            elif isinstance(v, bool):
                event_data[k] = str(v).lower()
            else:
                event_data[k] = str(v)
        
        await self.redis.xadd(self.stream_name, event_data)
        
        return event_id
    
    async def simulate_events(self, event_type: str, count: int = 1) -> int:
        """Simulate security events for testing"""
        simulated = 0
        
        for i in range(count):
            event = self._generate_test_event(event_type)
            await self.ingest_event(event)
            simulated += 1
            await asyncio.sleep(0.01)  # Small delay
        
        return simulated
    
    def _generate_test_event(self, event_type: str) -> Dict:
        """Generate test security event"""
        users = ['user1', 'user2', 'user3', 'admin', 'attacker']
        ips = ['192.168.1.100', '10.0.0.50', '203.0.113.42', '198.51.100.15']
        
        base_event = {
            'user_id': random.choice(users),
            'ip_address': random.choice(ips),
            'user_agent': 'Mozilla/5.0 (Test Client)',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        if event_type == 'failed_login':
            base_event.update({
                'event_type': 'authentication',
                'action': 'login',
                'resource': '/auth/login',
                'success': False,
                'metadata': {'reason': 'invalid_password'}
            })
        elif event_type == 'unusual_access':
            base_event.update({
                'event_type': 'data_access',
                'action': 'bulk_read',
                'resource': '/api/customers',
                'success': True,
                'metadata': {'records_accessed': random.randint(500, 2000)}
            })
        elif event_type == 'privilege_escalation':
            base_event.update({
                'event_type': 'authorization',
                'action': 'role_change',
                'resource': '/admin/users',
                'success': False,
                'metadata': {'attempted_role': 'admin', 'current_role': 'user'}
            })
        else:  # normal activity
            base_event.update({
                'event_type': 'api_access',
                'action': 'read',
                'resource': '/api/profile',
                'success': True,
                'metadata': {}
            })
        
        return base_event
