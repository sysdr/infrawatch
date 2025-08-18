#!/usr/bin/env python3
"""
Data Population Script for Metrics Data Models System
Populates the database with realistic infrastructure and application metrics
"""

import sys
import os

# Add the backend directory to the Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from datetime import datetime, timedelta, timezone
import random
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.metrics import Base, MetricsRaw, MetricCategories, RetentionPolicies, MetricIndexes
from services.metrics_service import MetricsService

# Database configuration
DATABASE_URL = "postgresql://metrics_user:metrics_pass@localhost:5432/metrics_db"

def create_engine_and_session():
    """Create database engine and session"""
    try:
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return engine, SessionLocal
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return None, None

def populate_metric_categories(db_session):
    """Populate metric categories"""
    print("📊 Populating metric categories...")
    
    categories = [
        {
            'category_name': 'system.cpu',
            'description': 'CPU utilization and performance metrics',
            'metric_type': 'gauge',
            'default_retention_days': 90,
            'aggregation_intervals': '["1m", "5m", "1h", "1d"]',
            'tags_whitelist': '["host", "cpu_core", "environment"]',
            'is_active': True
        },
        {
            'category_name': 'system.memory',
            'description': 'Memory usage and performance metrics',
            'metric_type': 'gauge',
            'default_retention_days': 90,
            'aggregation_intervals': '["1m", "5m", "1h", "1d"]',
            'tags_whitelist': '["host", "memory_type", "environment"]',
            'is_active': True
        },
        {
            'category_name': 'system.disk',
            'description': 'Disk I/O and space utilization metrics',
            'metric_type': 'gauge',
            'default_retention_days': 90,
            'aggregation_intervals': '["1m", "5m", "1h", "1d"]',
            'tags_whitelist': '["host", "device", "mount_point", "environment"]',
            'is_active': True
        },
        {
            'category_name': 'system.network',
            'description': 'Network throughput and connection metrics',
            'metric_type': 'counter',
            'default_retention_days': 60,
            'aggregation_intervals': '["1m", "5m", "1h", "1d"]',
            'tags_whitelist': '["host", "interface", "direction", "environment"]',
            'is_active': True
        },
        {
            'category_name': 'application.performance',
            'description': 'Application response time and throughput',
            'metric_type': 'histogram',
            'default_retention_days': 30,
            'aggregation_intervals': '["1m", "5m", "1h"]',
            'tags_whitelist': '["service", "endpoint", "method", "environment"]',
            'is_active': True
        },
        {
            'category_name': 'application.business',
            'description': 'Business metrics and KPIs',
            'metric_type': 'gauge',
            'default_retention_days': 365,
            'aggregation_intervals': '["1h", "1d", "1w", "1M"]',
            'tags_whitelist': '["region", "customer_type", "product"]',
            'is_active': True
        }
    ]
    
    for cat_data in categories:
        cat_data['aggregation_intervals'] = json.dumps(json.loads(cat_data['aggregation_intervals']))
        cat_data['tags_whitelist'] = json.dumps(json.loads(cat_data['tags_whitelist']))
        
        category = MetricCategories(**cat_data)
        db_session.add(category)
    
    db_session.commit()
    print(f"✅ Created {len(categories)} metric categories")

def populate_retention_policies(db_session):
    """Populate retention policies"""
    print("📋 Populating retention policies...")
    
    policies = [
        {
            'policy_name': 'realtime_metrics',
            'metric_pattern': r'^system\.(cpu|memory|disk|network)\..*',
            'retention_days': 7,
            'aggregation_strategy': 'avg',
            'priority': 10,
            'conditions': '{"environment": "production"}',
            'is_active': True
        },
        {
            'policy_name': 'application_metrics',
            'metric_pattern': r'^application\.(performance|business)\..*',
            'retention_days': 30,
            'aggregation_strategy': 'avg',
            'priority': 20,
            'conditions': '{"environment": "production"}',
            'is_active': True
        },
        {
            'policy_name': 'long_term_metrics',
            'metric_pattern': r'^application\.business\..*',
            'retention_days': 365,
            'aggregation_strategy': 'avg',
            'priority': 30,
            'conditions': '{"environment": "production"}',
            'is_active': True
        }
    ]
    
    for policy_data in policies:
        policy_data['conditions'] = json.dumps(json.loads(policy_data['conditions']))
        
        policy = RetentionPolicies(**policy_data)
        db_session.add(policy)
    
    db_session.commit()
    print(f"✅ Created {len(policies)} retention policies")

def generate_system_metrics(start_time, end_time, interval_minutes=1):
    """Generate realistic system metrics"""
    metrics = []
    current_time = start_time
    
    hosts = ['web-server-01', 'web-server-02', 'db-server-01', 'cache-server-01']
    environments = ['production', 'staging', 'development']
    
    while current_time <= end_time:
        for host in hosts:
            for env in environments:
                # CPU metrics
                cpu_usage = random.uniform(20, 95)
                cpu_idle = 100 - cpu_usage
                cpu_iowait = random.uniform(0, 15)
                
                metrics.extend([
                    {
                        'timestamp': current_time,
                        'metric_name': 'system.cpu.usage',
                        'metric_type': 'gauge',
                        'value': cpu_usage,
                        'tags': {'host': host, 'cpu_core': 'all', 'environment': env},
                        'labels': {'unit': 'percent'}
                    },
                    {
                        'timestamp': current_time,
                        'metric_name': 'system.cpu.idle',
                        'metric_type': 'gauge',
                        'value': cpu_idle,
                        'tags': {'host': host, 'cpu_core': 'all', 'environment': env},
                        'labels': {'unit': 'percent'}
                    },
                    {
                        'timestamp': current_time,
                        'metric_name': 'system.cpu.iowait',
                        'metric_type': 'gauge',
                        'value': cpu_iowait,
                        'tags': {'host': host, 'cpu_core': 'all', 'environment': env},
                        'labels': {'unit': 'percent'}
                    }
                ])
                
                # Memory metrics
                memory_used = random.uniform(60, 95)
                memory_available = 100 - memory_used
                swap_used = random.uniform(0, 30)
                
                metrics.extend([
                    {
                        'timestamp': current_time,
                        'metric_name': 'system.memory.used',
                        'metric_type': 'gauge',
                        'value': memory_used,
                        'tags': {'host': host, 'memory_type': 'ram', 'environment': env},
                        'labels': {'unit': 'percent'}
                    },
                    {
                        'timestamp': current_time,
                        'metric_name': 'system.memory.available',
                        'metric_type': 'gauge',
                        'value': memory_available,
                        'tags': {'host': host, 'memory_type': 'ram', 'environment': env},
                        'labels': {'unit': 'percent'}
                    },
                    {
                        'timestamp': current_time,
                        'metric_name': 'system.memory.swap_used',
                        'metric_type': 'gauge',
                        'value': swap_used,
                        'tags': {'host': host, 'memory_type': 'swap', 'environment': env},
                        'labels': {'unit': 'percent'}
                    }
                ])
                
                # Disk metrics
                disk_usage = random.uniform(40, 90)
                disk_read_bytes = random.uniform(1000000, 10000000)
                disk_write_bytes = random.uniform(500000, 5000000)
                
                metrics.extend([
                    {
                        'timestamp': current_time,
                        'metric_name': 'system.disk.usage',
                        'metric_type': 'gauge',
                        'value': disk_usage,
                        'tags': {'host': host, 'device': '/dev/sda1', 'mount_point': '/', 'environment': env},
                        'labels': {'unit': 'percent'}
                    },
                    {
                        'timestamp': current_time,
                        'metric_name': 'system.disk.read_bytes',
                        'metric_type': 'counter',
                        'value': disk_read_bytes,
                        'tags': {'host': host, 'device': '/dev/sda1', 'environment': env},
                        'labels': {'unit': 'bytes'}
                    },
                    {
                        'timestamp': current_time,
                        'metric_name': 'system.disk.write_bytes',
                        'metric_type': 'counter',
                        'value': disk_write_bytes,
                        'tags': {'host': host, 'device': '/dev/sda1', 'environment': env},
                        'labels': {'unit': 'bytes'}
                    }
                ])
                
                # Network metrics
                network_rx_bytes = random.uniform(1000000, 10000000)
                network_tx_bytes = random.uniform(500000, 5000000)
                network_connections = random.randint(100, 1000)
                
                metrics.extend([
                    {
                        'timestamp': current_time,
                        'metric_name': 'system.network.rx_bytes',
                        'metric_type': 'counter',
                        'value': network_rx_bytes,
                        'tags': {'host': host, 'interface': 'eth0', 'direction': 'in', 'environment': env},
                        'labels': {'unit': 'bytes'}
                    },
                    {
                        'timestamp': current_time,
                        'metric_name': 'system.network.tx_bytes',
                        'metric_type': 'counter',
                        'value': network_tx_bytes,
                        'tags': {'host': host, 'interface': 'eth0', 'direction': 'out', 'environment': env},
                        'labels': {'unit': 'bytes'}
                    },
                    {
                        'timestamp': current_time,
                        'metric_name': 'system.network.connections',
                        'metric_type': 'gauge',
                        'value': network_connections,
                        'tags': {'host': host, 'interface': 'eth0', 'environment': env},
                        'labels': {'unit': 'count'}
                    }
                ])
        
        current_time += timedelta(minutes=interval_minutes)
    
    return metrics

def generate_application_metrics(start_time, end_time, interval_minutes=1):
    """Generate realistic application metrics"""
    metrics = []
    current_time = start_time
    
    services = ['user-service', 'order-service', 'payment-service', 'inventory-service']
    endpoints = ['/api/users', '/api/orders', '/api/payments', '/api/inventory']
    methods = ['GET', 'POST', 'PUT', 'DELETE']
    environments = ['production', 'staging']
    
    while current_time <= end_time:
        for service in services:
            for env in environments:
                # Response time metrics
                response_time = random.uniform(50, 500)
                response_time_p95 = response_time * random.uniform(1.5, 3.0)
                response_time_p99 = response_time * random.uniform(2.0, 5.0)
                
                metrics.extend([
                    {
                        'timestamp': current_time,
                        'metric_name': 'application.performance.response_time',
                        'metric_type': 'histogram',
                        'value': response_time,
                        'tags': {'service': service, 'endpoint': '/api/health', 'method': 'GET', 'environment': env},
                        'labels': {'unit': 'milliseconds'}
                    },
                    {
                        'timestamp': current_time,
                        'metric_name': 'application.performance.response_time_p95',
                        'metric_type': 'gauge',
                        'value': response_time_p95,
                        'tags': {'service': service, 'endpoint': '/api/health', 'method': 'GET', 'environment': env},
                        'labels': {'unit': 'milliseconds'}
                    },
                    {
                        'timestamp': current_time,
                        'metric_name': 'application.performance.response_time_p99',
                        'metric_type': 'gauge',
                        'value': response_time_p99,
                        'tags': {'service': service, 'endpoint': '/api/health', 'method': 'GET', 'environment': env},
                        'labels': {'unit': 'milliseconds'}
                    }
                ])
                
                # Throughput metrics
                requests_per_second = random.uniform(100, 1000)
                error_rate = random.uniform(0.1, 5.0)
                
                metrics.extend([
                    {
                        'timestamp': current_time,
                        'metric_name': 'application.performance.requests_per_second',
                        'metric_type': 'gauge',
                        'value': requests_per_second,
                        'tags': {'service': service, 'endpoint': '/api/health', 'method': 'GET', 'environment': env},
                        'labels': {'unit': 'requests_per_second'}
                    },
                    {
                        'timestamp': current_time,
                        'metric_name': 'application.performance.error_rate',
                        'metric_type': 'gauge',
                        'value': error_rate,
                        'tags': {'service': service, 'endpoint': '/api/health', 'method': 'GET', 'environment': env},
                        'labels': {'unit': 'percent'}
                    }
                ])
                
                # Business metrics
                if service == 'order-service':
                    orders_per_minute = random.randint(10, 100)
                    revenue_per_minute = random.uniform(1000, 10000)
                    
                    metrics.extend([
                        {
                            'timestamp': current_time,
                            'metric_name': 'application.business.orders_per_minute',
                            'metric_type': 'gauge',
                            'value': orders_per_minute,
                            'tags': {'service': service, 'region': 'us-east-1', 'customer_type': 'retail', 'environment': env},
                            'labels': {'unit': 'orders_per_minute'}
                        },
                        {
                            'timestamp': current_time,
                            'metric_name': 'application.business.revenue_per_minute',
                            'metric_type': 'gauge',
                            'value': revenue_per_minute,
                            'tags': {'service': service, 'region': 'us-east-1', 'customer_type': 'retail', 'environment': env},
                            'labels': {'unit': 'dollars'}
                        }
                    ])
        
        current_time += timedelta(minutes=interval_minutes)
    
    return metrics

def populate_metrics_data(db_session, start_time, end_time):
    """Populate the database with metrics data"""
    print("📈 Generating and storing metrics data...")
    
    # Generate system metrics (every minute for the last 24 hours)
    system_metrics = generate_system_metrics(start_time, end_time, interval_minutes=1)
    print(f"📊 Generated {len(system_metrics)} system metrics")
    
    # Generate application metrics (every minute for the last 24 hours)
    app_metrics = generate_application_metrics(start_time, end_time, interval_minutes=1)
    print(f"📱 Generated {len(app_metrics)} application metrics")
    
    # Combine all metrics
    all_metrics = system_metrics + app_metrics
    print(f"🔢 Total metrics to store: {len(all_metrics)}")
    
    # Store metrics in batches
    batch_size = 1000
    metrics_service = MetricsService(db_session)
    
    for i in range(0, len(all_metrics), batch_size):
        batch = all_metrics[i:i + batch_size]
        try:
            metric_ids = metrics_service.batch_store_metrics(batch)
            print(f"✅ Stored batch {i//batch_size + 1}/{(len(all_metrics) + batch_size - 1)//batch_size} ({len(batch)} metrics)")
        except Exception as e:
            print(f"❌ Failed to store batch {i//batch_size + 1}: {e}")
            continue
    
    db_session.commit()
    print(f"🎉 Successfully populated database with {len(all_metrics)} metrics")

def main():
    """Main function to populate the database"""
    print("🚀 Starting Metrics Data Population...")
    
    # Create database connection
    engine, SessionLocal = create_engine_and_session()
    if not engine:
        print("❌ Cannot proceed without database connection")
        return
    
    # Create tables if they don't exist
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created/verified")
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return
    
    # Create session
    db_session = SessionLocal()
    
    try:
        # Populate reference data
        populate_metric_categories(db_session)
        populate_retention_policies(db_session)
        
        # Calculate time range (last 24 hours)
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=24)
        
        print(f"⏰ Generating data from {start_time} to {end_time}")
        
        # Populate metrics data
        populate_metrics_data(db_session, start_time, end_time)
        
        print("🎯 Data population completed successfully!")
        print(f"📊 Time range: {start_time.strftime('%Y-%m-%d %H:%M:%S')} to {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("🔍 You can now query the metrics through the API or dashboard")
        
    except Exception as e:
        print(f"❌ Error during data population: {e}")
        db_session.rollback()
    finally:
        db_session.close()

if __name__ == "__main__":
    main()
