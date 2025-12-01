from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from sqlalchemy import select, func, and_, or_, case
from sqlalchemy.ext.asyncio import AsyncSession
from models.analytics_models import NotificationEvent, NotificationMetricHourly, NotificationMetricDaily
import logging

logger = logging.getLogger(__name__)

class AggregationService:
    """Service for aggregating notification metrics"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def aggregate_hourly_metrics(self, time_bucket: datetime):
        """Aggregate events for a specific hour"""
        end_time = time_bucket + timedelta(hours=1)
        
        # Query aggregated data
        query = select(
            func.date_trunc('hour', NotificationEvent.created_at).label('time_bucket'),
            NotificationEvent.channel,
            NotificationEvent.template_id,
            NotificationEvent.status,
            func.count().label('event_count'),
            func.avg(NotificationEvent.processing_time_ms).label('avg_processing_time')
        ).where(
            and_(
                NotificationEvent.created_at >= time_bucket,
                NotificationEvent.created_at < end_time
            )
        ).group_by(
            'time_bucket',
            NotificationEvent.channel,
            NotificationEvent.template_id,
            NotificationEvent.status
        )
        
        result = await self.db.execute(query)
        rows = result.all()
        
        # Insert or update aggregated metrics
        for row in rows:
            metric = NotificationMetricHourly(
                time_bucket=row.time_bucket,
                channel=row.channel,
                template_id=row.template_id,
                status=row.status,
                event_count=row.event_count,
                avg_processing_time=row.avg_processing_time
            )
            self.db.add(metric)
        
        await self.db.commit()
        logger.info(f"Aggregated {len(rows)} hourly metrics for {time_bucket}")
    
    async def aggregate_daily_metrics(self, date: datetime):
        """Aggregate hourly metrics into daily metrics"""
        end_date = date + timedelta(days=1)
        
        query = select(
            func.date_trunc('day', NotificationMetricHourly.time_bucket).label('date'),
            NotificationMetricHourly.channel,
            NotificationMetricHourly.template_id,
            NotificationMetricHourly.status,
            func.sum(NotificationMetricHourly.event_count).label('event_count'),
            func.avg(NotificationMetricHourly.avg_processing_time).label('avg_processing_time')
        ).where(
            and_(
                NotificationMetricHourly.time_bucket >= date,
                NotificationMetricHourly.time_bucket < end_date
            )
        ).group_by(
            'date',
            NotificationMetricHourly.channel,
            NotificationMetricHourly.template_id,
            NotificationMetricHourly.status
        )
        
        result = await self.db.execute(query)
        rows = result.all()
        
        for row in rows:
            metric = NotificationMetricDaily(
                date=row.date,
                channel=row.channel,
                template_id=row.template_id,
                status=row.status,
                event_count=row.event_count,
                avg_processing_time=row.avg_processing_time
            )
            self.db.add(metric)
        
        await self.db.commit()
        logger.info(f"Aggregated {len(rows)} daily metrics for {date}")
    
    async def query_metrics(
        self,
        metric: str,
        group_by: List[str],
        start: datetime,
        end: datetime,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """Query metrics with dynamic grouping and filtering"""
        
        # Determine which table to use based on time range
        time_diff = end - start
        if time_diff.days > 7:
            # Use daily metrics for longer periods
            table = NotificationMetricDaily
            time_col = NotificationMetricDaily.date
        else:
            # Use hourly metrics for shorter periods
            table = NotificationMetricHourly
            time_col = NotificationMetricHourly.time_bucket
        
        # Build SELECT columns
        select_cols = [time_col.label('time')]
        group_cols = [time_col]
        
        if 'channel' in group_by:
            select_cols.append(table.channel)
            group_cols.append(table.channel)
        
        if 'template_id' in group_by:
            select_cols.append(table.template_id)
            group_cols.append(table.template_id)
        
        if 'status' in group_by:
            select_cols.append(table.status)
            group_cols.append(table.status)
        
        # Add metric calculation
        if metric == 'event_count':
            select_cols.append(func.sum(table.event_count).label('value'))
        elif metric == 'avg_processing_time':
            select_cols.append(func.avg(table.avg_processing_time).label('value'))
        elif metric == 'delivery_rate':
            # Calculate delivery rate as delivered / (delivered + failed)
            select_cols.append(
                (func.sum(
                    case((table.status == 'delivered', table.event_count), else_=0)
                ) * 100.0 / func.nullif(func.sum(table.event_count), 0)).label('value')
            )
        
        # Build query
        query = select(*select_cols).where(
            and_(time_col >= start, time_col < end)
        )
        
        # Apply filters
        if filters:
            conditions = []
            if 'channel' in filters:
                conditions.append(table.channel == filters['channel'])
            if 'status' in filters:
                conditions.append(table.status == filters['status'])
            if 'template_id' in filters:
                conditions.append(table.template_id == filters['template_id'])
            
            if conditions:
                query = query.where(and_(*conditions))
        
        query = query.group_by(*group_cols).order_by(time_col)
        
        result = await self.db.execute(query)
        rows = result.all()
        
        return [dict(row._mapping) for row in rows]
