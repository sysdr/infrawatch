from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.models.metrics import MetricEntry
from app.schemas.metrics import MetricCreate, MetricQuery, MetricResponse
from app.services.redis_service import redis_service
from typing import List, Optional
import structlog
import json
from datetime import datetime, timedelta

logger = structlog.get_logger()

class MetricsService:
    
    async def create_metric(self, db: AsyncSession, metric: MetricCreate) -> MetricEntry:
        db_metric = None
        try:
            # Store in database
            db_metric = MetricEntry(
                name=metric.name,
                value=metric.value,
                tags=json.dumps(metric.tags) if metric.tags else None,
                source=metric.source
            )
            db.add(db_metric)
            await db.flush()
            await db.refresh(db_metric)
            logger.info("Metric stored in database", name=metric.name, source=metric.source, value=metric.value)
        except Exception as e:
            logger.error("Database storage failed, using Redis only", error=str(e))
            # Create a mock metric for Redis storage
            db_metric = MetricEntry(
                id=0,  # Mock ID
                name=metric.name,
                value=metric.value,
                tags=json.dumps(metric.tags) if metric.tags else None,
                source=metric.source,
                timestamp=datetime.now()
            )
        
        # Store in Redis for real-time access
        redis_key = f"metric:{metric.name}:{metric.source}:{int(datetime.now().timestamp())}"
        redis_value = {
            "id": db_metric.id if db_metric else 0,
            "name": metric.name,
            "value": metric.value,
            "timestamp": db_metric.timestamp.isoformat() if db_metric else datetime.now().isoformat(),
            "tags": metric.tags,
            "source": metric.source
        }
        
        await redis_service.set_metric(redis_key, redis_value)
        logger.info("Metric created", name=metric.name, source=metric.source, value=metric.value)
        
        return db_metric
    
    async def create_metrics_batch(self, db: AsyncSession, metrics: List[MetricCreate]) -> List[MetricEntry]:
        db_metrics = []
        redis_operations = []
        
        for metric in metrics:
            db_metric = MetricEntry(
                name=metric.name,
                value=metric.value,
                tags=json.dumps(metric.tags) if metric.tags else None,
                source=metric.source
            )
            db_metrics.append(db_metric)
            
            # Prepare Redis operation
            redis_key = f"metric:{metric.name}:{metric.source}:{int(datetime.now().timestamp())}"
            redis_value = {
                "name": metric.name,
                "value": metric.value,
                "timestamp": datetime.now().isoformat(),
                "tags": metric.tags,
                "source": metric.source
            }
            redis_operations.append((redis_key, redis_value))
        
        # Bulk insert to database
        db.add_all(db_metrics)
        await db.flush()
        
        # Bulk operations to Redis
        for redis_key, redis_value in redis_operations:
            await redis_service.set_metric(redis_key, redis_value)
        
        logger.info("Metrics batch created", count=len(metrics))
        return db_metrics
    
    async def query_metrics(self, db: AsyncSession, query: MetricQuery) -> List[MetricResponse]:
        try:
            # Build query
            stmt = select(MetricEntry)
            
            conditions = []
            if query.name:
                conditions.append(MetricEntry.name == query.name)
            if query.source:
                conditions.append(MetricEntry.source == query.source)
            if query.start_time:
                conditions.append(MetricEntry.timestamp >= query.start_time)
            if query.end_time:
                conditions.append(MetricEntry.timestamp <= query.end_time)
            
            if conditions:
                stmt = stmt.where(and_(*conditions))
            
            stmt = stmt.order_by(MetricEntry.timestamp.desc())
            stmt = stmt.offset(query.offset).limit(query.limit)
            
            result = await db.execute(stmt)
            metrics = result.scalars().all()
            
            return [MetricResponse.from_orm(metric) for metric in metrics]
        except Exception as e:
            logger.error("Database query failed, returning empty list", error=str(e))
            return []
    
    async def get_realtime_metrics(self, pattern: str = "metric:*") -> dict:
        """Get latest metrics from Redis for real-time dashboard"""
        return await redis_service.get_latest_metrics(pattern)
    
    async def get_metric_summary(self, db: AsyncSession, name: str, hours: int = 24) -> dict:
        """Get statistical summary for a metric over time period"""
        try:
            start_time = datetime.now() - timedelta(hours=hours)
            
            stmt = select(
                func.min(MetricEntry.value).label('min_value'),
                func.max(MetricEntry.value).label('max_value'),
                func.avg(MetricEntry.value).label('avg_value'),
                func.count(MetricEntry.value).label('count')
            ).where(
                and_(
                    MetricEntry.name == name,
                    MetricEntry.timestamp >= start_time
                )
            )
            
            result = await db.execute(stmt)
            summary = result.first()
            
            return {
                "name": name,
                "min_value": float(summary.min_value) if summary.min_value else 0,
                "max_value": float(summary.max_value) if summary.max_value else 0,
                "avg_value": float(summary.avg_value) if summary.avg_value else 0,
                "count": summary.count or 0,
                "period_hours": hours
            }
        except Exception as e:
            logger.error("Database summary query failed, returning default values", error=str(e))
            return {
                "name": name,
                "min_value": 0,
                "max_value": 0,
                "avg_value": 0,
                "count": 0,
                "period_hours": hours
            }

metrics_service = MetricsService()
