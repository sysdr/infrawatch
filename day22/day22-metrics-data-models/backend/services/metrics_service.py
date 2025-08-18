from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, text, desc
from models.metrics import MetricsRaw, MetricCategories, RetentionPolicies, MetricAggregations, MetricIndexes
import re
import json

class MetricsService:
    def __init__(self, db: Session):
        self.db = db

    def store_metric(self, metric_data: Dict[str, Any]) -> str:
        """Store a single metric point"""
        
        # Apply retention policy
        retention_tier, expires_at = self._calculate_retention(
            metric_data['metric_name'], 
            metric_data.get('tags', {})
        )
        
        metric = MetricsRaw(
            timestamp=metric_data['timestamp'],
            metric_name=metric_data['metric_name'],
            metric_type=metric_data.get('metric_type', 'gauge'),
            value=float(metric_data['value']),
            tags=json.dumps(metric_data.get('tags', {})),
            labels=json.dumps(metric_data.get('labels', {})),
            retention_tier=retention_tier,
            expires_at=expires_at
        )
        
        self.db.add(metric)
        
        # Update metric index
        self._update_metric_index(metric_data['metric_name'], metric_data.get('metric_type', 'gauge'))
        
        return str(metric.id)

    def batch_store_metrics(self, metrics_data: List[Dict[str, Any]]) -> List[str]:
        """Store multiple metrics efficiently"""
        
        metrics = []
        for metric_data in metrics_data:
            retention_tier, expires_at = self._calculate_retention(
                metric_data['metric_name'], 
                metric_data.get('tags', {})
            )
            
            metric = MetricsRaw(
                timestamp=metric_data['timestamp'],
                metric_name=metric_data['metric_name'],
                metric_type=metric_data.get('metric_type', 'gauge'),
                value=float(metric_data['value']),
                tags=json.dumps(metric_data.get('tags', {})),
                labels=json.dumps(metric_data.get('labels', {})),
                retention_tier=retention_tier,
                expires_at=expires_at
            )
            metrics.append(metric)

        self.db.add_all(metrics)
        self.db.flush()
        
        # Update indexes
        for metric_data in metrics_data:
            self._update_metric_index(
                metric_data['metric_name'], 
                metric_data.get('metric_type', 'gauge')
            )
        
        return [str(m.id) for m in metrics]

    def query_metrics(self, 
                           metric_name: str,
                           start_time: datetime,
                           end_time: datetime,
                           tags: Dict[str, str] = None) -> List[Dict]:
        """Query metrics with time range and tag filtering"""
        
        query = self.db.query(MetricsRaw).filter(
            and_(
                MetricsRaw.metric_name == metric_name,
                MetricsRaw.timestamp >= start_time,
                MetricsRaw.timestamp <= end_time
            )
        )
        
        if tags:
            for key, value in tags.items():
                # For SQLite, we need to parse JSON text and search
                query = query.filter(MetricsRaw.tags.contains(f'"{key}": "{value}"'))
        
        results = query.order_by(MetricsRaw.timestamp).all()
        
        return [
            {
                'timestamp': r.timestamp.isoformat(),
                'value': r.value,
                'tags': json.loads(r.tags) if r.tags else {},
                'labels': json.loads(r.labels) if r.labels else {}
            }
            for r in results
        ]

    def get_aggregated_metrics(self, 
                                   metric_name: str,
                                   interval: str,
                                   start_time: datetime,
                                   end_time: datetime) -> List[Dict]:
        """Get pre-computed aggregations"""
        
        results = self.db.query(MetricAggregations).filter(
            and_(
                MetricAggregations.metric_name == metric_name,
                MetricAggregations.interval == interval,
                MetricAggregations.timestamp >= start_time,
                MetricAggregations.timestamp <= end_time
            )
        ).order_by(MetricAggregations.timestamp).all()
        
        return [
            {
                'timestamp': r.timestamp.isoformat(),
                'avg': r.avg_value,
                'min': r.min_value,
                'max': r.max_value,
                'sum': r.sum_value,
                'count': r.count_value,
                'p95': r.p95_value,
                'p99': r.p99_value
            }
            for r in results
        ]

    def _calculate_retention(self, metric_name: str, tags: Dict) -> tuple:
        """Calculate retention tier and expiry based on policies"""
        
        policies = self.db.query(RetentionPolicies).filter(
            RetentionPolicies.is_active == True
        ).order_by(RetentionPolicies.priority).all()
        
        for policy in policies:
            if re.match(policy.metric_pattern, metric_name):
                expires_at = datetime.now(timezone.utc) + timedelta(days=policy.retention_days)
                
                if policy.retention_days <= 7:
                    return 'realtime', expires_at
                elif policy.retention_days <= 30:
                    return 'recent', expires_at
                elif policy.retention_days <= 365:
                    return 'daily', expires_at
                else:
                    return 'archive', expires_at
        
        # Default retention
        return 'recent', datetime.now(timezone.utc) + timedelta(days=30)

    def _update_metric_index(self, metric_name: str, metric_type: str):
        """Update or create metric index entry"""
        
        index = self.db.query(MetricIndexes).filter(
            MetricIndexes.metric_name == metric_name
        ).first()
        
        if index:
            index.last_seen = datetime.now(timezone.utc)
            index.data_points_count += 1
        else:
            index = MetricIndexes(
                metric_name=metric_name,
                metric_type=metric_type,
                data_points_count=1
            )
            self.db.add(index)

    def search_metrics(self, search_term: str, limit: int = 50) -> List[Dict]:
        """Search for metrics by name pattern"""
        
        results = self.db.query(MetricIndexes).filter(
            and_(
                MetricIndexes.metric_name.ilike(f'%{search_term}%'),
                MetricIndexes.is_active == True
            )
        ).limit(limit).all()
        
        return [
            {
                'name': r.metric_name,
                'type': r.metric_type,
                'category': r.category,
                'last_seen': r.last_seen.isoformat() if r.last_seen else None,
                'data_points': r.data_points_count
            }
            for r in results
        ]

    def create_aggregations(self, interval: str = '1m'):
        """Create aggregated data for the specified interval"""
        
        interval_minutes = {
            '1m': 1, '5m': 5, '1h': 60, '1d': 1440
        }.get(interval, 1)
        
        # Get metrics that need aggregation
        end_time = datetime.now(timezone.utc).replace(second=0, microsecond=0)
        start_time = end_time - timedelta(minutes=interval_minutes)
        
        # Aggregate by metric name
        query = text("""
            SELECT 
                metric_name,
                AVG(value) as avg_value,
                MIN(value) as min_value,
                MAX(value) as max_value,
                SUM(value) as sum_value,
                COUNT(value) as count_value,
                tags
            FROM metrics_raw 
            WHERE timestamp >= :start_time 
              AND timestamp < :end_time
            GROUP BY metric_name, tags
        """)
        
        results = self.db.execute(query, {
            'start_time': start_time,
            'end_time': end_time
        })
        
        aggregations = []
        for row in results:
            agg = MetricAggregations(
                metric_name=row.metric_name,
                interval=interval,
                timestamp=start_time,
                avg_value=row.avg_value,
                min_value=row.min_value,
                max_value=row.max_value,
                sum_value=row.sum_value,
                count_value=row.count_value,
                p95_value=None,  # SQLite doesn't have PERCENTILE_CONT
                p99_value=None,  # SQLite doesn't have PERCENTILE_CONT
                tags=row.tags or '{}'
            )
            aggregations.append(agg)
        
        if aggregations:
            self.db.add_all(aggregations)
