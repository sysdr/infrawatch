"""Automated Security Response System"""
import asyncio
import json
from datetime import datetime, timezone
from typing import Dict

from models.database import get_db

class AutoResponder:
    """Automated threat response engine"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.response_rules = self._load_response_rules()
        
    def _load_response_rules(self) -> Dict:
        """Load automated response policies"""
        return {
            'medium': {  # 40-60 severity
                'actions': ['log_enhanced', 'notify_team', 'increase_monitoring'],
                'description': 'Enhanced monitoring and team notification'
            },
            'high': {  # 60-80 severity
                'actions': ['reduce_privileges', 'require_mfa', 'block_operations'],
                'description': 'Privilege reduction and MFA requirement'
            },
            'critical': {  # 80+ severity
                'actions': ['suspend_account', 'block_ip', 'terminate_sessions', 'notify_executive'],
                'description': 'Immediate account suspension and executive notification'
            }
        }
    
    async def start_response(self):
        """Start automated response system"""
        print("Auto Responder started")
        
        # Subscribe to threat notifications
        pubsub = self.redis.pubsub()
        await pubsub.subscribe('security:threats:response')
        
        while True:
            try:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                
                if message and message['type'] == 'message':
                    threat = json.loads(message['data'])
                    await self.respond_to_threat(threat)
                    
            except Exception as e:
                print(f"Response error: {e}")
                await asyncio.sleep(1)
    
    async def respond_to_threat(self, threat: Dict):
        """Execute automated response to threat"""
        try:
            severity = threat['severity']
            threat_id = threat['threat_id']
            
            # Determine response level
            if severity >= 80:
                level = 'critical'
            elif severity >= 60:
                level = 'high'
            else:
                level = 'medium'
            
            # Execute response actions
            response_rule = self.response_rules[level]
            actions_taken = []
            
            for action in response_rule['actions']:
                result = await self.execute_action(action, threat)
                actions_taken.append({
                    'action': action,
                    'result': result,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
            
            # Log response
            await self.log_response(threat_id, level, actions_taken)
            
            # Update threat status
            await self.update_threat_status(threat_id, 'responded', actions_taken)
            
            print(f"Responded to {threat_id} with {level} level actions")
            
        except Exception as e:
            print(f"Threat response error: {e}")
    
    async def execute_action(self, action: str, threat: Dict) -> str:
        """Execute specific response action"""
        user_id = threat.get('user_id')
        ip_address = threat.get('ip_address')
        
        if action == 'log_enhanced':
            # Enable verbose logging for user/IP
            await self.redis.setex(f"enhanced_log:{user_id}", 3600, "true")
            return "Enhanced logging enabled for 1 hour"
        
        elif action == 'notify_team':
            # Send notification to security team (simulated)
            notification = {
                'type': 'security_alert',
                'threat_id': threat['threat_id'],
                'severity': threat['severity'],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            await self.redis.publish('notifications:security_team', json.dumps(notification))
            return "Security team notified"
        
        elif action == 'increase_monitoring':
            # Reduce monitoring thresholds for user
            await self.redis.setex(f"high_sensitivity:{user_id}", 3600, "true")
            return "Monitoring sensitivity increased for 1 hour"
        
        elif action == 'reduce_privileges':
            # Temporarily reduce user privileges
            await self.redis.setex(f"reduced_privileges:{user_id}", 1800, "true")
            return "Privileges reduced for 30 minutes"
        
        elif action == 'require_mfa':
            # Force MFA re-authentication
            await self.redis.setex(f"require_mfa:{user_id}", 3600, "true")
            return "MFA re-authentication required"
        
        elif action == 'block_operations':
            # Block sensitive operations
            await self.redis.setex(f"block_sensitive_ops:{user_id}", 1800, "true")
            return "Sensitive operations blocked for 30 minutes"
        
        elif action == 'suspend_account':
            # Suspend user account
            await self.redis.setex(f"account_suspended:{user_id}", 7200, "true")
            return "Account suspended for 2 hours"
        
        elif action == 'block_ip':
            # Add IP to blocklist
            await self.redis.sadd("blocked_ips", ip_address)
            await self.redis.setex(f"ip_blocked:{ip_address}", 3600, "true")
            return f"IP {ip_address} blocked for 1 hour"
        
        elif action == 'terminate_sessions':
            # Terminate all active sessions
            await self.redis.delete(f"sessions:{user_id}")
            return "All user sessions terminated"
        
        elif action == 'notify_executive':
            # Send executive notification (simulated)
            notification = {
                'type': 'critical_security_incident',
                'threat_id': threat['threat_id'],
                'severity': threat['severity'],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            await self.redis.publish('notifications:executives', json.dumps(notification))
            return "Executive team notified"
        
        return f"Action {action} simulated"
    
    async def log_response(self, threat_id: str, level: str, actions: list):
        """Log response actions to database"""
        db = await get_db()
        
        query = """
            INSERT INTO response_actions (
                threat_id, response_level, actions, timestamp
            ) VALUES ($1, $2, $3, $4)
        """
        
        await db.execute(
            query,
            threat_id,
            level,
            json.dumps(actions),
            datetime.now(timezone.utc)
        )
    
    async def update_threat_status(self, threat_id: str, status: str, actions: list):
        """Update threat status after response"""
        db = await get_db()
        
        query = """
            UPDATE threats
            SET status = $1,
                automated_response = true,
                response_actions = $2,
                responded_at = $3
            WHERE threat_id = $4
        """
        
        await db.execute(
            query,
            status,
            json.dumps(actions),
            datetime.now(timezone.utc),
            threat_id
        )
