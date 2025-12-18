from app.core.database import AsyncSessionLocal
from app.models.metrics import MetricData
from datetime import datetime, timedelta
import random
import numpy as np

class DataGenerator:
    def __init__(self):
        self.services = ['api-gateway', 'auth-service', 'user-service', 'order-service', 'payment-service']
        self.endpoints = {
            'api-gateway': ['/health', '/metrics', '/status'],
            'auth-service': ['/login', '/logout', '/verify', '/refresh'],
            'user-service': ['/users', '/users/{id}', '/users/{id}/profile'],
            'order-service': ['/orders', '/orders/{id}', '/orders/{id}/status'],
            'payment-service': ['/payments', '/payments/{id}', '/refunds']
        }
        self.regions = ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1']
        self.environments = ['production', 'staging']
        self.metrics = ['latency', 'error_rate', 'request_count', 'cpu_usage', 'memory_usage']
        self.statuses = ['healthy', 'degraded', 'critical']
    
    async def generate_sample_data(self):
        async with AsyncSessionLocal() as session:
            # Check if data already exists
            from sqlalchemy import select, func
            result = await session.execute(select(func.count(MetricData.id)))
            count = result.scalar()
            
            if count > 0:
                print(f"✅ Database already has {count} records, skipping generation")
                return
            
            print("📊 Generating sample metric data...")
            
            # Generate data for last 7 days
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=7)
            
            records = []
            current_time = start_time
            
            while current_time <= end_time:
                for service in self.services:
                    for endpoint in self.endpoints[service]:
                        for region in self.regions:
                            for environment in self.environments:
                                for metric in self.metrics:
                                    # Generate realistic values with patterns
                                    base_value = self._get_base_value(metric, service, endpoint)
                                    noise = np.random.normal(0, base_value * 0.1)
                                    
                                    # Add time-based patterns (higher during business hours)
                                    hour = current_time.hour
                                    time_multiplier = 1.0
                                    if 9 <= hour <= 17:  # Business hours
                                        time_multiplier = 1.5
                                    elif 0 <= hour <= 6:  # Night
                                        time_multiplier = 0.7
                                    
                                    value = max(0, base_value * time_multiplier + noise)
                                    
                                    # Determine status based on value
                                    status = self._determine_status(metric, value)
                                    
                                    record = MetricData(
                                        timestamp=current_time,
                                        service=service,
                                        endpoint=endpoint,
                                        region=region,
                                        environment=environment,
                                        metric_name=metric,
                                        value=round(value, 2),
                                        status=status
                                    )
                                    records.append(record)
                
                current_time += timedelta(minutes=5)
                
                # Batch insert every 1000 records
                if len(records) >= 1000:
                    session.add_all(records)
                    await session.commit()
                    print(f"  ✓ Inserted {len(records)} records (up to {current_time})")
                    records = []
            
            # Insert remaining records
            if records:
                session.add_all(records)
                await session.commit()
                print(f"  ✓ Inserted final {len(records)} records")
            
            print("✅ Sample data generation complete")
    
    def _get_base_value(self, metric: str, service: str, endpoint: str) -> float:
        """Get realistic base values for different metrics"""
        if metric == 'latency':
            # Some endpoints are naturally slower
            if 'payment' in service or 'order' in service:
                return random.uniform(200, 500)
            return random.uniform(50, 150)
        elif metric == 'error_rate':
            return random.uniform(0.1, 2.0)
        elif metric == 'request_count':
            return random.uniform(100, 1000)
        elif metric == 'cpu_usage':
            return random.uniform(20, 70)
        elif metric == 'memory_usage':
            return random.uniform(30, 80)
        return random.uniform(10, 100)
    
    def _determine_status(self, metric: str, value: float) -> str:
        """Determine health status based on metric value"""
        if metric == 'latency':
            if value > 500:
                return 'critical'
            elif value > 300:
                return 'degraded'
            return 'healthy'
        elif metric == 'error_rate':
            if value > 5:
                return 'critical'
            elif value > 2:
                return 'degraded'
            return 'healthy'
        elif metric in ['cpu_usage', 'memory_usage']:
            if value > 85:
                return 'critical'
            elif value > 70:
                return 'degraded'
            return 'healthy'
        return 'healthy'
