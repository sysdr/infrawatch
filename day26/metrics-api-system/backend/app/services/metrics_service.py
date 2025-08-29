from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, text
import pandas as pd
import numpy as np
from app.models.metric import Metric, AggregatedMetric
from app.models.schemas import (
    MetricQueryRequest, MetricQueryResponse, MetricDataPoint,
    AggregationType, IntervalType
)
from app.services.cache_service import cache_service
import structlog

logger = structlog.get_logger()

class MetricsService:
    
    def __init__(self):
        self.interval_mapping = {
            '1m': timedelta(minutes=1),
            '5m': timedelta(minutes=5),
            '15m': timedelta(minutes=15),
            '1h': timedelta(hours=1),
            '1d': timedelta(days=1),
            '1w': timedelta(weeks=1)
        }
    
    async def query_metrics(self, db: Session, request: MetricQueryRequest) -> MetricQueryResponse:
        """Query metrics with caching and optimization"""
        
        # Check cache first
        cached_result = await cache_service.get_query_result(
            request.metric_name,
            request.start_time,
            request.end_time,
            request.interval.value,
            [agg.value for agg in request.aggregations]
        )
        
        if cached_result:
            return MetricQueryResponse(**cached_result, cache_hit=True)
        
        # Query database
        data_points = await self._query_database(db, request)
        
        response = MetricQueryResponse(
            metric_name=request.metric_name,
            start_time=request.start_time,
            end_time=request.end_time,
            interval=request.interval.value,
            data_points=data_points,
            total_points=len(data_points),
            cache_hit=False
        )
        
        # Cache the result
        await cache_service.set_query_result(
            request.metric_name,
            request.start_time,
            request.end_time,
            request.interval.value,
            [agg.value for agg in request.aggregations],
            response.dict(exclude={'cache_hit'})
        )
        
        return response
    
    async def _query_database(self, db: Session, request: MetricQueryRequest) -> List[MetricDataPoint]:
        """Query database with optimized aggregation"""
        
        # First try aggregated metrics table for better performance
        if len(request.aggregations) == 1:
            agg_data = await self._query_aggregated_metrics(db, request)
            if agg_data:
                return agg_data
        
        # Fallback to raw metrics with real-time aggregation
        return await self._query_raw_metrics(db, request)
    
    async def _query_aggregated_metrics(self, db: Session, request: MetricQueryRequest) -> Optional[List[MetricDataPoint]]:
        """Query pre-aggregated metrics"""
        try:
            query = db.query(AggregatedMetric).filter(
                and_(
                    AggregatedMetric.metric_name == request.metric_name,
                    AggregatedMetric.interval_start >= request.start_time,
                    AggregatedMetric.interval_end <= request.end_time,
                    AggregatedMetric.interval_duration == request.interval.value,
                    AggregatedMetric.aggregation_type == request.aggregations[0].value
                )
            ).order_by(AggregatedMetric.interval_start).limit(request.limit)
            
            results = query.all()
            
            if not results:
                return None
            
            data_points = []
            for result in results:
                data_points.append(MetricDataPoint(
                    timestamp=result.interval_start,
                    value=result.value,
                    aggregation_type=result.aggregation_type
                ))
            
            logger.info("Used aggregated metrics", count=len(data_points))
            return data_points
            
        except Exception as e:
            logger.error("Aggregated query error", error=str(e))
            return None
    
    async def _query_raw_metrics(self, db: Session, request: MetricQueryRequest) -> List[MetricDataPoint]:
        """Query raw metrics with real-time aggregation"""
        
        interval_delta = self.interval_mapping[request.interval.value]
        
        # Generate time buckets
        current_time = request.start_time
        time_buckets = []
        
        while current_time < request.end_time:
            time_buckets.append(current_time)
            current_time += interval_delta
        
        data_points = []
        
        for bucket_start in time_buckets:
            bucket_end = bucket_start + interval_delta
            
            # Query metrics in this time bucket
            bucket_query = db.query(Metric).filter(
                and_(
                    Metric.name == request.metric_name,
                    Metric.timestamp >= bucket_start,
                    Metric.timestamp < bucket_end
                )
            )
            
            metrics_in_bucket = bucket_query.all()
            
            if not metrics_in_bucket:
                continue
            
            values = [m.value for m in metrics_in_bucket]
            
            # Apply aggregations
            for agg_type in request.aggregations:
                agg_value = self._calculate_aggregation(values, agg_type)
                
                data_points.append(MetricDataPoint(
                    timestamp=bucket_start,
                    value=agg_value,
                    aggregation_type=agg_type.value
                ))
        
        # Sort and limit
        data_points.sort(key=lambda x: x.timestamp)
        return data_points[:request.limit]
    
    def _calculate_aggregation(self, values: List[float], agg_type: AggregationType) -> float:
        """Calculate aggregation value"""
        if not values:
            return 0.0
        
        if agg_type == AggregationType.avg:
            return np.mean(values)
        elif agg_type == AggregationType.sum:
            return np.sum(values)
        elif agg_type == AggregationType.count:
            return len(values)
        elif agg_type == AggregationType.min:
            return np.min(values)
        elif agg_type == AggregationType.max:
            return np.max(values)
        elif agg_type == AggregationType.p50:
            return np.percentile(values, 50)
        elif agg_type == AggregationType.p95:
            return np.percentile(values, 95)
        elif agg_type == AggregationType.p99:
            return np.percentile(values, 99)
        
        return 0.0
    
    async def export_metrics(self, db: Session, request) -> Dict[str, Any]:
        """Export metrics in specified format"""
        
        # Convert export request to query request
        query_request = MetricQueryRequest(
            metric_name=request.metric_name,
            start_time=request.start_time,
            end_time=request.end_time,
            interval=request.interval,
            aggregations=[request.aggregation],
            limit=10000  # Maximum limit for exports
        )
        
        result = await self.query_metrics(db, query_request)
        
        # Format data
        export_data = []
        for point in result.data_points:
            export_data.append({
                'timestamp': point.timestamp.isoformat(),
                'metric_name': result.metric_name,
                'value': point.value,
                'aggregation': point.aggregation_type
            })
        
        return {
            'data': export_data,
            'metadata': {
                'metric_name': result.metric_name,
                'start_time': result.start_time.isoformat(),
                'end_time': result.end_time.isoformat(),
                'interval': result.interval,
                'total_points': result.total_points,
                'export_format': request.format.value,
                'generated_at': datetime.utcnow().isoformat()
            }
        }

metrics_service = MetricsService()
