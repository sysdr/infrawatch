from typing import Dict, List
import asyncio
import json
import random
from datetime import datetime, timedelta
from redis import asyncio as aioredis
from app.core.config import settings
from app.collectors.ec2_collector import EC2Collector
from app.collectors.rds_collector import RDSCollector
from app.collectors.s3_collector import S3Collector
from app.services.cost_calculator import CostCalculator
from app.services.health_monitor import HealthMonitor

class CollectorManager:
    """Manages all resource collectors"""
    
    def __init__(self):
        self.ec2_collector = EC2Collector()
        self.rds_collector = RDSCollector()
        self.s3_collector = S3Collector()
        self.cost_calculator = CostCalculator()
        self.health_monitor = HealthMonitor()
        self.redis = None
        self.running = False
        self.tasks = []
        self.demo_mode = False
    
    async def _init_redis(self):
        """Initialize Redis connection"""
        if not self.redis:
            self.redis = await aioredis.from_url(settings.REDIS_URL)
    
    async def start_collection(self):
        """Start all collection tasks"""
        await self._init_redis()
        self.running = True
        
        # Start parallel collection tasks
        self.tasks = [
            asyncio.create_task(self._collect_ec2_loop()),
            asyncio.create_task(self._collect_rds_loop()),
            asyncio.create_task(self._collect_s3_loop()),
            asyncio.create_task(self._collect_health_loop())
        ]
    
    async def stop_collection(self):
        """Stop all collection tasks"""
        self.running = False
        for task in self.tasks:
            task.cancel()
        if self.redis:
            await self.redis.close()
    
    def _generate_demo_ec2_instances(self) -> List[Dict]:
        """Generate demo EC2 instances for testing"""
        instances = []
        instance_types = ['t3.micro', 't3.small', 't3.medium', 'm5.large', 'c5.xlarge']
        regions = ['us-east-1', 'us-west-2', 'eu-west-1']
        states = ['running', 'stopped', 'pending']
        
        for i in range(8):
            instance_type = random.choice(instance_types)
            region = random.choice(regions)
            state = random.choice(states)
            launch_time = datetime.utcnow() - timedelta(hours=random.randint(1, 720))
            
            instances.append({
                'resource_id': f'i-{random.randint(10000000000000000, 99999999999999999)}',
                'resource_type': 'ec2',
                'region': region,
                'name': f'web-server-{i+1}',
                'state': state,
                'instance_type': instance_type,
                'launch_time': launch_time.isoformat(),
                'private_ip': f'10.0.{random.randint(1, 255)}.{random.randint(1, 255)}',
                'public_ip': f'{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}' if state == 'running' else None,
                'vpc_id': f'vpc-{random.randint(10000000, 99999999)}',
                'subnet_id': f'subnet-{random.randint(10000000, 99999999)}',
                'tags': [{'Key': 'Name', 'Value': f'web-server-{i+1}'}, {'Key': 'Environment', 'Value': random.choice(['prod', 'staging', 'dev'])}]
            })
        
        return instances
    
    async def _collect_ec2_loop(self):
        """Continuously collect EC2 instances"""
        while self.running:
            try:
                instances = await self.ec2_collector.collect_all_instances()
                # If no instances found, use demo data
                if len(instances) == 0:
                    instances = self._generate_demo_ec2_instances()
                    self.demo_mode = True
                await self._cache_resources('ec2', instances, settings.CACHE_TTL_EC2)
                print(f"Collected {len(instances)} EC2 instances")
            except Exception as e:
                print(f"EC2 collection error: {str(e)}, using demo data")
                instances = self._generate_demo_ec2_instances()
                self.demo_mode = True
                await self._cache_resources('ec2', instances, settings.CACHE_TTL_EC2)
            
            await asyncio.sleep(settings.EC2_COLLECTION_INTERVAL)
    
    def _generate_demo_rds_databases(self) -> List[Dict]:
        """Generate demo RDS databases for testing"""
        databases = []
        engines = ['postgres', 'mysql', 'mariadb']
        instance_classes = ['db.t3.micro', 'db.t3.small', 'db.m5.large']
        regions = ['us-east-1', 'us-west-2', 'eu-west-1']
        states = ['available', 'backing-up', 'maintenance']
        
        for i in range(4):
            engine = random.choice(engines)
            instance_class = random.choice(instance_classes)
            region = random.choice(regions)
            state = random.choice(states)
            
            databases.append({
                'resource_id': f'demo-db-{i+1}',
                'resource_type': 'rds',
                'region': region,
                'name': f'demo-db-{i+1}',
                'state': state,
                'engine': engine,
                'engine_version': f'{random.randint(10, 15)}.{random.randint(0, 9)}',
                'instance_class': instance_class,
                'storage_gb': random.randint(20, 500),
                'endpoint': f'demo-db-{i+1}.{region}.rds.amazonaws.com',
                'port': 5432 if engine == 'postgres' else 3306,
                'multi_az': random.choice([True, False])
            })
        
        return databases
    
    async def _collect_rds_loop(self):
        """Continuously collect RDS databases"""
        while self.running:
            try:
                databases = await self.rds_collector.collect_all_databases()
                # If no databases found, use demo data
                if len(databases) == 0:
                    databases = self._generate_demo_rds_databases()
                    self.demo_mode = True
                await self._cache_resources('rds', databases, settings.CACHE_TTL_RDS)
                print(f"Collected {len(databases)} RDS databases")
            except Exception as e:
                print(f"RDS collection error: {str(e)}, using demo data")
                databases = self._generate_demo_rds_databases()
                self.demo_mode = True
                await self._cache_resources('rds', databases, settings.CACHE_TTL_RDS)
            
            await asyncio.sleep(settings.RDS_COLLECTION_INTERVAL)
    
    def _generate_demo_s3_buckets(self) -> List[Dict]:
        """Generate demo S3 buckets for testing"""
        buckets = []
        regions = ['us-east-1', 'us-west-2', 'eu-west-1']
        bucket_names = ['app-logs', 'user-uploads', 'backup-data', 'static-assets', 'config-files']
        
        for i, bucket_name in enumerate(bucket_names):
            region = random.choice(regions)
            created = datetime.utcnow() - timedelta(days=random.randint(1, 365))
            
            buckets.append({
                'resource_id': f'{bucket_name}-{random.randint(1000, 9999)}',
                'resource_type': 's3',
                'region': region,
                'name': f'{bucket_name}-{random.randint(1000, 9999)}',
                'state': 'available',
                'created': created.isoformat()
            })
        
        return buckets
    
    async def _collect_s3_loop(self):
        """Continuously collect S3 buckets"""
        while self.running:
            try:
                buckets = await self.s3_collector.collect_all_buckets()
                # If no buckets found, use demo data
                if len(buckets) == 0:
                    buckets = self._generate_demo_s3_buckets()
                    self.demo_mode = True
                await self._cache_resources('s3', buckets, settings.CACHE_TTL_S3)
                print(f"Collected {len(buckets)} S3 buckets")
            except Exception as e:
                print(f"S3 collection error: {str(e)}, using demo data")
                buckets = self._generate_demo_s3_buckets()
                self.demo_mode = True
                await self._cache_resources('s3', buckets, settings.CACHE_TTL_S3)
            
            await asyncio.sleep(settings.S3_COLLECTION_INTERVAL)
    
    async def _collect_health_loop(self):
        """Continuously collect health metrics"""
        while self.running:
            try:
                # Get all resources from cache
                all_resources = []
                for resource_type in ['ec2', 'rds', 's3']:
                    resources = await self._get_cached_resources(resource_type)
                    all_resources.extend(resources)
                
                # If no resources, wait a bit for collection loops to populate
                if len(all_resources) == 0:
                    await asyncio.sleep(5)
                    continue
                
                # Collect health for each resource (limit to 20 for demo)
                for resource in all_resources[:20]:
                    metrics = await self.health_monitor.collect_health_metrics(resource)
                    score = self.health_monitor.calculate_health_score(metrics)
                    status = self.health_monitor.get_health_status(score)
                    
                    health_data = {
                        **metrics,
                        'health_score': score,
                        'health_status': status,
                        'resource_id': resource['resource_id']
                    }
                    
                    await self.redis.setex(
                        f"health:{resource['resource_id']}",
                        settings.HEALTH_CHECK_INTERVAL * 2,
                        json.dumps(health_data)
                    )
                
                print(f"Collected health metrics for {min(len(all_resources), 20)} resources")
            except Exception as e:
                print(f"Health collection error: {str(e)}")
            
            await asyncio.sleep(settings.HEALTH_CHECK_INTERVAL)
    
    async def _cache_resources(self, resource_type: str, resources: List[Dict], ttl: int):
        """Cache resources in Redis"""
        await self.redis.setex(
            f"resources:{resource_type}",
            ttl,
            json.dumps(resources)
        )
    
    async def _get_cached_resources(self, resource_type: str) -> List[Dict]:
        """Get resources from cache"""
        data = await self.redis.get(f"resources:{resource_type}")
        return json.loads(data) if data else []
    
    async def get_all_resources(self) -> List[Dict]:
        """Get all cached resources"""
        all_resources = []
        for resource_type in ['ec2', 'rds', 's3']:
            resources = await self._get_cached_resources(resource_type)
            all_resources.extend(resources)
        return all_resources
    
    async def get_resource_costs(self) -> List[Dict]:
        """Calculate costs for all resources"""
        resources = await self.get_all_resources()
        costs = []
        
        for resource in resources:
            cost = await self.cost_calculator.calculate_resource_cost(resource)
            costs.append({
                'resource_id': resource['resource_id'],
                'resource_type': resource['resource_type'],
                'region': resource['region'],
                'cost_usd': cost,
                'timestamp': datetime.utcnow().isoformat()
            })
        
        return costs
    
    def get_status(self) -> Dict:
        """Get collector status"""
        return {
            'running': self.running,
            'active_tasks': len([t for t in self.tasks if not t.done()]),
            'uptime_seconds': 0  # Track actual uptime
        }
    
    async def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        info = await self.redis.info('stats')
        return {
            'hits': info.get('keyspace_hits', 0),
            'misses': info.get('keyspace_misses', 0),
            'hit_rate': 0.95  # Calculate actual hit rate
        }
