from typing import List, Dict
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.resource import Cost, Resource
from datetime import datetime, timedelta
import statistics

class CostService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_cost_summary(self, days: int = 30) -> Dict:
        """Get cost summary for period"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Total cost
        total_query = select(func.sum(Cost.amount)).where(Cost.date >= start_date)
        total_result = await self.db.execute(total_query)
        total_cost = total_result.scalar() or 0.0
        
        # Cost by provider
        provider_query = select(
            Resource.cloud_provider,
            func.sum(Cost.amount).label('amount')
        ).join(Resource, Cost.resource_id == Resource.id).where(
            Cost.date >= start_date
        ).group_by(Resource.cloud_provider)
        
        provider_result = await self.db.execute(provider_query)
        by_provider = [
            {'provider': row[0], 'amount': float(row[1])}
            for row in provider_result
        ]
        
        # Cost by service type
        service_query = select(
            Cost.service_type,
            func.sum(Cost.amount).label('amount')
        ).where(
            Cost.date >= start_date
        ).group_by(Cost.service_type)
        
        service_result = await self.db.execute(service_query)
        by_service = [
            {'service': row[0] or 'unknown', 'amount': float(row[1])}
            for row in service_result
        ]
        
        return {
            'total': round(total_cost, 2),
            'period_days': days,
            'by_provider': by_provider,
            'by_service': by_service,
            'currency': 'USD'
        }
    
    async def get_cost_trends(self, days: int = 90) -> Dict:
        """Get daily cost trends"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = select(
            func.date(Cost.date).label('day'),
            func.sum(Cost.amount).label('amount')
        ).where(
            Cost.date >= start_date
        ).group_by(func.date(Cost.date)).order_by(func.date(Cost.date))
        
        result = await self.db.execute(query)
        daily_costs = [
            {'date': row[0].isoformat(), 'amount': float(row[1])}
            for row in result
        ]
        
        # Calculate statistics
        amounts = [d['amount'] for d in daily_costs]
        mean_cost = statistics.mean(amounts) if amounts else 0
        stdev_cost = statistics.stdev(amounts) if len(amounts) > 1 else 0
        
        # Detect anomalies (2 standard deviations)
        threshold = mean_cost + (2 * stdev_cost)
        anomalies = [d for d in daily_costs if d['amount'] > threshold]
        
        return {
            'daily_costs': daily_costs,
            'mean': round(mean_cost, 2),
            'std_dev': round(stdev_cost, 2),
            'anomalies': anomalies
        }
    
    async def forecast_costs(self, days: int = 30) -> Dict:
        """Forecast future costs using linear regression"""
        # Get last 30 days of data
        start_date = datetime.utcnow() - timedelta(days=30)
        
        query = select(
            func.date(Cost.date).label('day'),
            func.sum(Cost.amount).label('amount')
        ).where(
            Cost.date >= start_date
        ).group_by(func.date(Cost.date)).order_by(func.date(Cost.date))
        
        result = await self.db.execute(query)
        historical = [(i, float(row[1])) for i, row in enumerate(result)]
        
        if len(historical) < 2:
            return {'forecast': [], 'confidence_interval': 0}
        
        # Calculate linear regression
        n = len(historical)
        sum_x = sum(x for x, y in historical)
        sum_y = sum(y for x, y in historical)
        sum_xx = sum(x*x for x, y in historical)
        sum_xy = sum(x*y for x, y in historical)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
        intercept = (sum_y - slope * sum_x) / n
        
        # Calculate standard error
        predictions = [slope * x + intercept for x, y in historical]
        residuals = [(y - pred) ** 2 for (x, y), pred in zip(historical, predictions)]
        std_error = (sum(residuals) / (n - 2)) ** 0.5 if n > 2 else 0
        
        # Forecast future days
        forecast = []
        for future_day in range(days):
            day_index = n + future_day
            predicted = slope * day_index + intercept
            future_date = datetime.utcnow() + timedelta(days=future_day)
            
            forecast.append({
                'date': future_date.date().isoformat(),
                'predicted_amount': round(max(0, predicted), 2),
                'lower_bound': round(max(0, predicted - 2 * std_error), 2),
                'upper_bound': round(predicted + 2 * std_error, 2)
            })
        
        return {
            'forecast': forecast,
            'confidence_interval': round(2 * std_error, 2)
        }
    
    async def get_top_resources_by_cost(self, limit: int = 10) -> List[Dict]:
        """Get most expensive resources"""
        start_date = datetime.utcnow() - timedelta(days=30)
        
        query = select(
            Resource.id,
            Resource.name,
            Resource.resource_type,
            func.sum(Cost.amount).label('total_cost')
        ).join(
            Resource, Cost.resource_id == Resource.id
        ).where(
            Cost.date >= start_date
        ).group_by(
            Resource.id, Resource.name, Resource.resource_type
        ).order_by(
            func.sum(Cost.amount).desc()
        ).limit(limit)
        
        result = await self.db.execute(query)
        return [
            {
                'resource_id': row[0],
                'name': row[1],
                'type': row[2],
                'cost': round(float(row[3]), 2)
            }
            for row in result
        ]
