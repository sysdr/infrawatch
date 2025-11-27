from app.models.database import SessionLocal, engine, Base
from app.models.notification import Notification, NotificationType
from datetime import datetime, timedelta
import random

def seed_notifications(count: int = 1000):
    # Create tables first
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_count = db.query(Notification).count()
        if existing_count > 0:
            print(f"Database already has {existing_count} notifications. Skipping seed.")
            return
            
        print(f"Seeding {count} notifications...")
        
        notification_types = list(NotificationType)
        titles = [
            "System Alert",
            "New Message",
            "Task Completed",
            "Warning Notice",
            "Security Update",
            "Performance Report",
            "User Activity",
            "Server Status"
        ]
        
        messages = [
            "This is a test notification message",
            "Your task has been completed successfully",
            "Please review the latest security updates",
            "System performance is optimal",
            "New user registered on the platform",
            "Database backup completed",
            "API rate limit approaching threshold",
            "Cache cleared successfully"
        ]
        
        for i in range(count):
            notification = Notification(
                user_id=random.randint(1, 100),
                title=random.choice(titles),
                message=random.choice(messages),
                notification_type=random.choice(notification_types),
                is_read=random.choice([0, 1]),
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            db.add(notification)
            
            if (i + 1) % 100 == 0:
                db.commit()
                print(f"Seeded {i + 1}/{count} notifications...")
                
        db.commit()
        print(f"Successfully seeded {count} notifications!")
        
    finally:
        db.close()

if __name__ == "__main__":
    seed_notifications(10000)
