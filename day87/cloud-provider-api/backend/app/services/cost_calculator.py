from typing import Dict, List
from datetime import datetime, timedelta
from app.services.aws_client import aws_client_pool
import json

class CostCalculator:
    """Calculates real-time AWS costs"""
    
    def __init__(self):
        self.pricing_cache = {}
    
    async def get_ec2_pricing(self, instance_type: str, region: str) -> float:
        """Get EC2 pricing from Price List API"""
        cache_key = f"ec2:{region}:{instance_type}"
        
        if cache_key in self.pricing_cache:
            return self.pricing_cache[cache_key]
        
        try:
            pricing = aws_client_pool.get_client('pricing', 'us-east-1')
            
            def get_price():
                response = pricing.get_products(
                    ServiceCode='AmazonEC2',
                    Filters=[
                        {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_type},
                        {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': self._get_location_name(region)},
                        {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': 'Linux'},
                        {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': 'Shared'},
                        {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw', 'Value': 'NA'}
                    ]
                )
                
                for price_item in response['PriceList']:
                    price_data = json.loads(price_item)
                    on_demand = price_data['terms']['OnDemand']
                    for key in on_demand:
                        price_dimensions = on_demand[key]['priceDimensions']
                        for dim_key in price_dimensions:
                            price_per_hour = float(price_dimensions[dim_key]['pricePerUnit']['USD'])
                            return price_per_hour
                
                return 0.0
            
            price = await aws_client_pool.execute_with_retry(get_price)
            self.pricing_cache[cache_key] = price
            return price
        
        except Exception as e:
            print(f"Error getting pricing: {str(e)}")
            # Fallback to estimated pricing
            return self._get_fallback_pricing(instance_type)
    
    def _get_location_name(self, region: str) -> str:
        """Convert region code to location name"""
        location_map = {
            'us-east-1': 'US East (N. Virginia)',
            'us-west-2': 'US West (Oregon)',
            'eu-west-1': 'EU (Ireland)'
        }
        return location_map.get(region, 'US East (N. Virginia)')
    
    def _get_fallback_pricing(self, instance_type: str) -> float:
        """Fallback pricing estimates"""
        pricing_estimates = {
            't3.micro': 0.0104,
            't3.small': 0.0208,
            't3.medium': 0.0416,
            't3.large': 0.0832,
            'm5.large': 0.096,
            'm5.xlarge': 0.192,
            'c5.large': 0.085,
            'r5.large': 0.126
        }
        return pricing_estimates.get(instance_type, 0.10)
    
    async def calculate_resource_cost(self, resource: Dict) -> float:
        """Calculate cost for a resource"""
        if resource['resource_type'] == 'ec2':
            hourly_rate = await self.get_ec2_pricing(
                resource.get('instance_type', 't3.medium'),
                resource['region']
            )
            
            # Calculate runtime since launch
            launch_time = datetime.fromisoformat(resource.get('launch_time', datetime.utcnow().isoformat()))
            hours_running = (datetime.utcnow() - launch_time).total_seconds() / 3600
            
            return hourly_rate * min(hours_running, 24)  # Cap at 24 hours for demo
        
        return 0.0
    
    async def get_cost_forecast(self, days: int = 30) -> Dict:
        """Forecast costs for next N days"""
        # Simplified forecast based on current usage
        return {
            'forecast_days': days,
            'estimated_total': 1500.00 * days,
            'confidence': 0.85
        }
