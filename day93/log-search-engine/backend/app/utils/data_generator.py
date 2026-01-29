from faker import Faker
from app.models.log import Log
from app.core.database import SessionLocal, engine
from sqlalchemy import text
from datetime import datetime, timedelta
import random

fake = Faker()

LEVELS = ['info', 'warning', 'error', 'critical', 'debug']
SERVICES = ['api', 'web', 'worker', 'database', 'cache', 'auth', 'payment']
MESSAGES = [
    'Request processed successfully',
    'Connection timeout to database',
    'User authentication failed',
    'Payment processed',
    'Cache miss for key',
    'OutOfMemoryError in service',
    'Rate limit exceeded',
    'API response time exceeded threshold',
    'Database query slow',
    'Connection pool exhausted'
]

def generate_logs(count: int = 1000):
    """Generate sample logs"""
    db = SessionLocal()
    
    # Enable extensions
    db.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
    db.execute(text("CREATE EXTENSION IF NOT EXISTS btree_gin;"))
    db.commit()
    
    print(f"Generating {count} sample logs...")
    
    logs = []
    base_time = datetime.utcnow() - timedelta(days=7)
    
    for i in range(count):
        timestamp = base_time + timedelta(
            seconds=random.randint(0, 7 * 24 * 3600)
        )
        
        level = random.choice(LEVELS)
        service = random.choice(SERVICES)
        message = random.choice(MESSAGES)
        
        log = Log(
            timestamp=timestamp,
            level=level,
            service=service,
            message=message,
            user_id=f"user_{random.randint(1, 100)}",
            request_id=fake.uuid4(),
            metadata=f'{{"ip": "{fake.ipv4()}", "duration_ms": {random.randint(10, 1000)}}}'
        )
        logs.append(log)
        
        if len(logs) >= 100:
            db.bulk_save_objects(logs)
            db.commit()
            logs = []
            print(f"Generated {i + 1}/{count} logs...")
    
    if logs:
        db.bulk_save_objects(logs)
        db.commit()
    
    # Update search vectors
    print("Updating search vectors...")
    db.execute(text("""
        UPDATE logs 
        SET search_vector = to_tsvector('english', 
            coalesce(level, '') || ' ' || 
            coalesce(service, '') || ' ' || 
            coalesce(message, '')
        )
        WHERE search_vector IS NULL;
    """))
    db.commit()
    
    print(f"Successfully generated {count} logs!")
    db.close()

if __name__ == "__main__":
    generate_logs(10000)
