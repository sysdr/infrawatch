"""Threat Detection and Analysis Engine"""
import asyncio
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
import math
from collections import defaultdict

from models.database import get_db, fetchrow_query, fetch_query, execute_query, is_sqlite
from utils.baseline_engine import BaselineEngine

class ThreatAnalyzer:
    """Multi-layer threat detection and analysis"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.baseline_engine = BaselineEngine(redis_client)
        self.detection_rules = self._load_detection_rules()
        self.threat_scores = defaultdict(float)
        
    def _load_detection_rules(self) -> List[Dict]:
        """Load threat detection signatures"""
        return [
            {
                'name': 'brute_force_login',
                'pattern': 'failed_login',
                'threshold': 5,
                'window': 300,  # 5 minutes
                'severity': 70
            },
            {
                'name': 'bulk_data_access',
                'pattern': 'bulk_read',
                'threshold': 1000,
                'window': 60,
                'severity': 65
            },
            {
                'name': 'privilege_escalation_attempt',
                'pattern': 'role_change',
                'threshold': 3,
                'window': 600,
                'severity': 85
            },
            {
                'name': 'unusual_time_access',
                'pattern': 'access_off_hours',
                'threshold': 1,
                'window': 3600,
                'severity': 50
            }
        ]
    
    async def start_analysis(self):
        """Start continuous threat analysis"""
        print("Threat Analyzer started")
        
        # Subscribe to security events
        pubsub = self.redis.pubsub()
        await pubsub.subscribe('security:events:analysis')
        
        while True:
            try:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                
                if message and message['type'] == 'message':
                    event = json.loads(message['data'])
                    await self.analyze_event(event)
                    
            except Exception as e:
                print(f"Analysis error: {e}")
                await asyncio.sleep(1)
    
    async def analyze_event(self, event: Dict):
        """Analyze security event for threats"""
        try:
            anomalies = []
            
            # Statistical baseline analysis
            baseline_score = await self.baseline_engine.check_baseline(event)
            if baseline_score > 40:
                anomalies.append({
                    'type': 'baseline_deviation',
                    'score': baseline_score,
                    'details': f"Unusual pattern detected (score: {baseline_score})"
                })
            
            # Signature-based detection
            signature_matches = await self.check_signatures(event)
            anomalies.extend(signature_matches)
            
            # Behavioral analysis
            behavior_score = await self.analyze_behavior(event)
            if behavior_score > 40:
                anomalies.append({
                    'type': 'behavioral_anomaly',
                    'score': behavior_score,
                    'details': f"Suspicious behavior pattern (score: {behavior_score})"
                })
            
            # Calculate aggregate threat score
            if anomalies:
                total_score = sum(a['score'] for a in anomalies)
                aggregate_score = min(100, total_score * 1.2)  # Amplify combined anomalies
                
                # Create threat if score is significant
                if aggregate_score >= 40:
                    await self.create_threat(event, anomalies, aggregate_score)
                    
        except Exception as e:
            print(f"Event analysis error: {e}")
    
    async def check_signatures(self, event: Dict) -> List[Dict]:
        """Check event against threat signatures"""
        matches = []
        user_id = event.get('user_id', 'anonymous')
        event_type = event.get('event_type', '')
        action = event.get('action', '')
        
        for rule in self.detection_rules:
            # Check if event matches pattern (check both event_type and action)
            pattern = rule['pattern']
            matches_pattern = False
            
            # Special pattern matching for different event types
            if pattern == 'failed_login':
                # Match failed login attempts
                matches_pattern = (event_type == 'authentication' and action == 'login' and not event.get('success', True))
            elif pattern == 'bulk_read':
                # Match bulk data access
                matches_pattern = (action == 'bulk_read' or 'bulk' in action.lower())
            elif pattern == 'role_change':
                # Match privilege escalation
                matches_pattern = (action == 'role_change' or 'role' in action.lower())
            else:
                # Generic pattern matching
                matches_pattern = (pattern in event_type or pattern in action)
            
            if matches_pattern:
                # Count occurrences in time window
                count = await self.count_pattern_occurrences(
                    user_id, 
                    pattern, 
                    rule['window']
                )
                
                if count >= rule['threshold']:
                    matches.append({
                        'type': rule['name'],
                        'score': rule['severity'],
                        'details': f"{rule['name']}: {count} occurrences in {rule['window']}s"
                    })
        
        return matches
    
    async def count_pattern_occurrences(self, user_id: str, pattern: str, window: int) -> int:
        """Count pattern occurrences within time window"""
        use_sqlite = is_sqlite()
        
        if use_sqlite:
            # SQLite syntax
            query = """
                SELECT COUNT(*) as count
                FROM security_events
                WHERE user_id = ?
                AND (event_type LIKE ? OR action LIKE ?)
                AND datetime(timestamp) > datetime('now', '-' || ? || ' seconds')
            """
            pattern_like = f'%{pattern}%'
            result = await fetchrow_query(query, user_id, pattern_like, pattern_like, window)
        else:
            # PostgreSQL syntax
            query = """
                SELECT COUNT(*) as count
                FROM security_events
                WHERE user_id = $1
                AND (event_type LIKE $2 OR action LIKE $2)
                AND timestamp > NOW() - INTERVAL '1 second' * $3
            """
            result = await fetchrow_query(query, user_id, f'%{pattern}%', window)
        
        return result.get('count', 0) if result else 0
    
    async def analyze_behavior(self, event: Dict) -> float:
        """Analyze behavioral patterns"""
        user_id = event.get('user_id')
        if not user_id:
            return 0
        
        score = 0
        
        # Check access time anomaly
        event_hour = datetime.fromisoformat(event['timestamp']).hour
        if event_hour < 6 or event_hour > 22:  # Outside business hours
            score += 30
        
        # Check rapid API calls
        recent_events = await self.get_recent_user_events(user_id, 60)
        if len(recent_events) > 50:  # More than 50 events per minute
            score += 40
        
        # Check resource access pattern
        if 'bulk' in event.get('action', '') or event.get('metadata', {}).get('records_accessed', 0) > 100:
            score += 35
        
        return min(100, score)
    
    async def get_recent_user_events(self, user_id: str, seconds: int) -> List:
        """Get recent events for user"""
        use_sqlite = is_sqlite()
        
        if use_sqlite:
            # SQLite syntax
            query = """
                SELECT * FROM security_events
                WHERE user_id = ?
                AND datetime(timestamp) > datetime('now', '-' || ? || ' seconds')
                ORDER BY timestamp DESC
            """
            events = await fetch_query(query, user_id, seconds)
        else:
            # PostgreSQL syntax
            query = """
                SELECT * FROM security_events
                WHERE user_id = $1
                AND timestamp > NOW() - INTERVAL '1 second' * $2
                ORDER BY timestamp DESC
            """
            events = await fetch_query(query, user_id, seconds)
        
        return events
    
    async def create_threat(self, event: Dict, anomalies: List[Dict], severity: float):
        """Create threat record"""
        use_sqlite = is_sqlite()
        attack_type = anomalies[0]['type'] if anomalies else 'unknown'
        threat_id = f"THR_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{event.get('user_id', 'anon')[:10]}"
        detected_at = datetime.now(timezone.utc).isoformat()
        anomalies_json = json.dumps(anomalies)
        
        if use_sqlite:
            # SQLite syntax - use ? placeholders
            query = """
                INSERT INTO threats (
                    threat_id, event_id, user_id, ip_address, attack_type,
                    severity, anomalies, detected_at, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            await execute_query(
                query,
                threat_id,
                event.get('event_id'),
                event.get('user_id'),
                event.get('ip_address'),
                attack_type,
                int(severity),
                anomalies_json,
                detected_at,
                'active'
            )
        else:
            # PostgreSQL syntax
            query = """
                INSERT INTO threats (
                    threat_id, event_id, user_id, ip_address, attack_type,
                    severity, anomalies, detected_at, status
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                RETURNING threat_id
            """
            await execute_query(
                query,
                threat_id,
                event.get('event_id'),
                event.get('user_id'),
                event.get('ip_address'),
                attack_type,
                int(severity),
                anomalies_json,
                detected_at,
                'active'
            )
        
        # Publish threat for response system
        threat_data = {
            'threat_id': threat_id,
            'severity': severity,
            'user_id': event.get('user_id'),
            'ip_address': event.get('ip_address'),
            'attack_type': attack_type
        }
        
        await self.redis.publish('security:threats:response', json.dumps(threat_data))
        
        print(f"Threat created: {threat_id} (severity: {severity})")
