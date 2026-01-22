from typing import List, Dict
import asyncio
from datetime import datetime
from app.services.aws_client import aws_client_pool
from app.core.config import settings

class EC2Collector:
    """Collects EC2 instance inventory across regions"""
    
    def __init__(self):
        self.regions = self._get_regions()
    
    def _get_regions(self) -> List[str]:
        """Get list of AWS regions"""
        try:
            ec2 = aws_client_pool.get_client('ec2', 'us-east-1')
            response = ec2.describe_regions()
            return [region['RegionName'] for region in response['Regions']]
        except:
            # Fallback to common regions
            return ['us-east-1', 'us-west-2', 'eu-west-1']
    
    async def collect_all_instances(self) -> List[Dict]:
        """Collect EC2 instances from all regions in parallel"""
        tasks = [self._collect_region(region) for region in self.regions]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        instances = []
        for result in results:
            if isinstance(result, list):
                instances.extend(result)
        
        return instances
    
    async def _collect_region(self, region: str) -> List[Dict]:
        """Collect EC2 instances from a single region"""
        try:
            ec2 = aws_client_pool.get_client('ec2', region)
            
            def describe():
                response = ec2.describe_instances()
                instances = []
                
                for reservation in response.get('Reservations', []):
                    for instance in reservation.get('Instances', []):
                        instances.append({
                            'resource_id': instance['InstanceId'],
                            'resource_type': 'ec2',
                            'region': region,
                            'name': self._get_instance_name(instance),
                            'state': instance['State']['Name'],
                            'instance_type': instance['InstanceType'],
                            'launch_time': instance['LaunchTime'].isoformat(),
                            'private_ip': instance.get('PrivateIpAddress'),
                            'public_ip': instance.get('PublicIpAddress'),
                            'vpc_id': instance.get('VpcId'),
                            'subnet_id': instance.get('SubnetId'),
                            'tags': instance.get('Tags', [])
                        })
                
                return instances
            
            return await aws_client_pool.execute_with_retry(describe)
        
        except Exception as e:
            print(f"Error collecting EC2 from {region}: {str(e)}")
            return []
    
    def _get_instance_name(self, instance: Dict) -> str:
        """Extract instance name from tags"""
        for tag in instance.get('Tags', []):
            if tag['Key'] == 'Name':
                return tag['Value']
        return instance['InstanceId']
    
    async def get_instance_metrics(self, instance_id: str, region: str) -> Dict:
        """Get CloudWatch metrics for an instance"""
        try:
            cloudwatch = aws_client_pool.get_client('cloudwatch', region)
            
            def get_metrics():
                # Get CPU utilization
                cpu_response = cloudwatch.get_metric_statistics(
                    Namespace='AWS/EC2',
                    MetricName='CPUUtilization',
                    Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                    StartTime=datetime.utcnow().replace(minute=0, second=0, microsecond=0),
                    EndTime=datetime.utcnow(),
                    Period=300,
                    Statistics=['Average']
                )
                
                cpu_avg = 0
                if cpu_response['Datapoints']:
                    cpu_avg = cpu_response['Datapoints'][-1]['Average']
                
                return {
                    'cpu_utilization': cpu_avg,
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            return await aws_client_pool.execute_with_retry(get_metrics)
        
        except Exception as e:
            return {'cpu_utilization': 0, 'error': str(e)}
