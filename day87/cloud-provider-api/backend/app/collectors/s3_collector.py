from typing import List, Dict
from app.services.aws_client import aws_client_pool

class S3Collector:
    """Collects S3 bucket inventory"""
    
    async def collect_all_buckets(self) -> List[Dict]:
        """Collect all S3 buckets"""
        try:
            s3 = aws_client_pool.get_client('s3')
            
            def list_buckets():
                response = s3.list_buckets()
                buckets = []
                
                for bucket in response.get('Buckets', []):
                    bucket_name = bucket['Name']
                    
                    # Get bucket location
                    try:
                        location = s3.get_bucket_location(Bucket=bucket_name)
                        region = location['LocationConstraint'] or 'us-east-1'
                    except:
                        region = 'us-east-1'
                    
                    buckets.append({
                        'resource_id': bucket_name,
                        'resource_type': 's3',
                        'region': region,
                        'name': bucket_name,
                        'state': 'available',
                        'created': bucket['CreationDate'].isoformat()
                    })
                
                return buckets
            
            return await aws_client_pool.execute_with_retry(list_buckets)
        
        except Exception as e:
            print(f"Error collecting S3 buckets: {str(e)}")
            return []
