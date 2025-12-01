import asyncio
from datetime import datetime, timedelta
import random
from database.db_config import AsyncSessionLocal, init_db
from models.analytics_models import NotificationEvent

async def seed_notification_events(days: int = 7, events_per_hour: int = 1000):
    """Seed database with sample notification events"""
    
    await init_db()
    
    async with AsyncSessionLocal() as db:
        channels = ['email', 'sms', 'push']
        statuses = ['sent', 'delivered', 'failed', 'bounced', 'opened', 'clicked']
        template_ids = [1, 2, 3, 4, 5]
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        
        current_time = start_time
        total_events = 0
        
        while current_time < end_time:
            # Generate events for this hour
            for _ in range(events_per_hour):
                # Vary event time within the hour
                event_time = current_time + timedelta(seconds=random.randint(0, 3599))
                
                # Realistic status distribution
                status_weights = [0.05, 0.85, 0.05, 0.02, 0.02, 0.01]
                status = random.choices(statuses, weights=status_weights)[0]
                
                # Channel distribution
                channel = random.choices(channels, weights=[0.5, 0.3, 0.2])[0]
                
                event = NotificationEvent(
                    created_at=event_time,
                    channel=channel,
                    template_id=random.choice(template_ids),
                    user_id=random.randint(1, 10000),
                    status=status,
                    processing_time_ms=random.randint(10, 500),
                    event_metadata={}
                )
                db.add(event)
                total_events += 1
            
            # Commit batch
            if total_events % 10000 == 0:
                await db.commit()
                print(f"Inserted {total_events} events...")
            
            current_time += timedelta(hours=1)
        
        await db.commit()
        print(f"Seeding complete! Inserted {total_events} events")

if __name__ == "__main__":
    asyncio.run(seed_notification_events(days=7, events_per_hour=1000))
