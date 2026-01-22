from typing import List, Dict
import asyncio
from app.services.aws_client import aws_client_pool

class RDSCollector:
    """Collects RDS database inventory"""
    
    def __init__(self):
        self.regions = ['us-east-1', 'us-west-2', 'eu-west-1']
    
    async def collect_all_databases(self) -> List[Dict]:
        """Collect RDS databases from all regions"""
        tasks = [self._collect_region(region) for region in self.regions]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        databases = []
        for result in results:
            if isinstance(result, list):
                databases.extend(result)
        
        return databases
    
    async def _collect_region(self, region: str) -> List[Dict]:
        """Collect RDS databases from a single region"""
        try:
            rds = aws_client_pool.get_client('rds', region)
            
            def describe():
                response = rds.describe_db_instances()
                databases = []
                
                for db in response.get('DBInstances', []):
                    databases.append({
                        'resource_id': db['DBInstanceIdentifier'],
                        'resource_type': 'rds',
                        'region': region,
                        'name': db['DBInstanceIdentifier'],
                        'state': db['DBInstanceStatus'],
                        'engine': db['Engine'],
                        'engine_version': db['EngineVersion'],
                        'instance_class': db['DBInstanceClass'],
                        'storage_gb': db['AllocatedStorage'],
                        'endpoint': db.get('Endpoint', {}).get('Address'),
                        'port': db.get('Endpoint', {}).get('Port'),
                        'multi_az': db['MultiAZ']
                    })
                
                return databases
            
            return await aws_client_pool.execute_with_retry(describe)
        
        except Exception as e:
            print(f"Error collecting RDS from {region}: {str(e)}")
            return []
