import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from config.database import SessionLocal, engine
from app.models.metric import Metric, Base
import asyncio

async def create_sample_metrics():
    """Create sample metrics data for testing"""
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if data already exists
        existing_count = db.query(Metric).count()
        if existing_count > 100:
            print(f"Sample data already exists ({existing_count} metrics)")
            return
        
        print("Creating sample metrics data...")
        
        # Generate metrics for last 7 days
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=7)
        
        metric_names = [
            'cpu_usage_percent',
            'memory_usage_percent', 
            'disk_io_ops',
            'network_bytes_in',
            'network_bytes_out',
            'response_time_ms',
            'error_rate_percent',
            'request_count'
        ]
        
        sources = ['web-server-1', 'web-server-2', 'api-server-1', 'database-1']
        
        current_time = start_time
        metrics_created = 0
        
        while current_time < end_time:
            for metric_name in metric_names:
                for source in sources:
                    # Generate realistic values based on metric type
                    if 'percent' in metric_name:
                        base_value = random.uniform(10, 90)
                        value = max(0, min(100, base_value + random.gauss(0, 10)))
                    elif 'response_time' in metric_name:
                        base_value = random.uniform(50, 200)
                        value = max(0, base_value + random.gauss(0, 50))
                    elif 'count' in metric_name:
                        value = max(0, int(random.gauss(100, 30)))
                    elif 'bytes' in metric_name:
                        value = max(0, random.expovariate(1/1000000))
                    else:
                        value = max(0, random.uniform(0, 1000))
                    
                    metric = Metric(
                        name=metric_name,
                        value=value,
                        timestamp=current_time,
                        source=source,
                        tags=f'{{"environment": "production", "service": "{source}"}}'
                    )
                    db.add(metric)
                    metrics_created += 1
            
            # Commit every 1000 metrics
            if metrics_created % 1000 == 0:
                db.commit()
                print(f"Created {metrics_created} metrics...")
            
            current_time += timedelta(minutes=5)
        
        db.commit()
        print(f"✅ Created {metrics_created} sample metrics")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()
