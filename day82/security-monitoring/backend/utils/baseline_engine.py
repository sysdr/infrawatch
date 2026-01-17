"""Behavioral baseline learning engine"""
from datetime import datetime, timedelta, timezone
from typing import Dict
import json
import math

from models.database import get_db, fetchrow_query, fetch_query, execute_query, is_sqlite

class BaselineEngine:
    """Statistical baseline analysis for anomaly detection"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        
    async def check_baseline(self, event: Dict) -> float:
        """Check event against user baseline and return anomaly score"""
        user_id = event.get('user_id')
        if not user_id:
            return 0
        
        score = 0
        
        # Check time-based baseline
        time_score = await self.check_time_baseline(user_id, event)
        score += time_score
        
        # Check geographic baseline
        geo_score = await self.check_geo_baseline(user_id, event)
        score += geo_score
        
        # Check volume baseline
        volume_score = await self.check_volume_baseline(user_id, event)
        score += volume_score
        
        return min(100, score)
    
    async def check_time_baseline(self, user_id: str, event: Dict) -> float:
        """Check if access time is unusual for user"""
        # Get user's typical access hours from baseline
        baseline = await self.get_baseline(user_id, 'access_hours')
        
        if not baseline:
            return 0
        
        event_time = datetime.fromisoformat(event['timestamp'])
        event_hour = event_time.hour
        
        # Check if hour is in typical range
        typical_hours = baseline.get('typical_hours', [])
        
        if not typical_hours:
            return 0
        
        if event_hour not in typical_hours:
            # Calculate deviation
            min_hour = min(typical_hours)
            max_hour = max(typical_hours)
            
            if event_hour < min_hour:
                deviation = min_hour - event_hour
            else:
                deviation = event_hour - max_hour
            
            # Score based on deviation (max 40 points)
            return min(40, deviation * 5)
        
        return 0
    
    async def check_geo_baseline(self, user_id: str, event: Dict) -> float:
        """Check if geographic location is unusual"""
        baseline = await self.get_baseline(user_id, 'geo_location')
        
        if not baseline:
            return 0
        
        event_country = event.get('country')
        event_city = event.get('city')
        
        typical_locations = baseline.get('typical_locations', [])
        
        # Check if location matches baseline
        for location in typical_locations:
            if location['country'] == event_country and location['city'] == event_city:
                return 0
        
        # New country is more suspicious
        if event_country not in [loc['country'] for loc in typical_locations]:
            return 50
        
        # Same country, different city is less suspicious
        return 25
    
    async def check_volume_baseline(self, user_id: str, event: Dict) -> float:
        """Check if activity volume is unusual"""
        # For now, return 0 to avoid database complexity
        # This can be enhanced later when we have sufficient baseline data
        return 0
        
        # Get baseline average
        baseline = await self.get_baseline(user_id, 'activity_volume')
        
        if not baseline:
            return 0
        
        avg_hourly = baseline.get('avg_hourly_events', 10)
        
        # Score based on deviation from average
        if recent_count > avg_hourly * 3:
            return 45
        elif recent_count > avg_hourly * 2:
            return 30
        
        return 0
    
    async def get_baseline(self, user_id: str, baseline_type: str) -> Dict:
        """Retrieve user baseline from database"""
        # For now, return empty dict - baseline creation needs more work
        # This allows signature-based detection to work
        return {}
    
    async def create_baseline(self, user_id: str, baseline_type: str) -> Dict:
        """Create initial baseline for user"""
        db = await get_db()
        
        if baseline_type == 'access_hours':
            # Analyze typical access hours
            query = """
                SELECT EXTRACT(HOUR FROM timestamp) as hour, COUNT(*) as count
                FROM security_events
                WHERE user_id = $1
                AND timestamp > NOW() - INTERVAL '30 days'
                GROUP BY hour
                ORDER BY count DESC
            """
            
            results = await db.fetch(query, user_id)
            
            if results:
                # Top hours representing 80% of activity
                total = sum(r['count'] for r in results)
                threshold = total * 0.8
                cumulative = 0
                typical_hours = []
                
                for row in results:
                    typical_hours.append(int(row['hour']))
                    cumulative += row['count']
                    if cumulative >= threshold:
                        break
                
                baseline_data = {'typical_hours': typical_hours}
            else:
                baseline_data = {'typical_hours': list(range(9, 18))}  # Default business hours
        
        elif baseline_type == 'geo_location':
            # Analyze typical locations
            query = """
                SELECT country, city, COUNT(*) as count
                FROM security_events
                WHERE user_id = $1
                AND timestamp > NOW() - INTERVAL '30 days'
                GROUP BY country, city
                ORDER BY count DESC
                LIMIT 5
            """
            
            results = await db.fetch(query, user_id)
            
            typical_locations = [
                {'country': r['country'], 'city': r['city']}
                for r in results if r['country'] and r['city']
            ]
            
            baseline_data = {'typical_locations': typical_locations or [{'country': 'US', 'city': 'Unknown'}]}
        
        elif baseline_type == 'activity_volume':
            # Calculate average activity
            query = """
                SELECT 
                    DATE_TRUNC('hour', timestamp) as hour_bucket,
                    COUNT(*) as count
                FROM security_events
                WHERE user_id = $1
                AND timestamp > NOW() - INTERVAL '30 days'
                GROUP BY hour_bucket
            """
            
            results = await db.fetch(query, user_id)
            
            if results:
                avg_hourly = sum(r['count'] for r in results) / len(results)
            else:
                avg_hourly = 10
            
            baseline_data = {'avg_hourly_events': avg_hourly}
        
        else:
            baseline_data = {}
        
        # Store baseline
        insert_query = """
            INSERT INTO user_baselines (user_id, baseline_type, baseline_data, valid_until)
            VALUES ($1, $2, $3, $4)
        """
        
        await db.execute(
            insert_query,
            user_id,
            baseline_type,
            baseline_data,
            datetime.now(timezone.utc) + timedelta(days=30)
        )
        
        return baseline_data
