from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func, text
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from ..models.alert_models import Alert, AlertStatus, AlertSeverity
import pandas as pd
from io import StringIO
import json

class AlertQueryService:
    def __init__(self, db: Session):
        self.db = db
    
    def search_alerts(
        self,
        query: Optional[str] = None,
        status: Optional[List[str]] = None,
        severity: Optional[List[str]] = None,
        source: Optional[List[str]] = None,
        service: Optional[List[str]] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Dict[str, Any]:
        
        # Base query
        base_query = self.db.query(Alert)
        
        # Text search
        if query:
            base_query = base_query.filter(
                or_(
                    Alert.title.ilike(f"%{query}%"),
                    Alert.description.ilike(f"%{query}%"),
                    Alert.source.ilike(f"%{query}%"),
                    Alert.service.ilike(f"%{query}%")
                )
            )
        
        # Status filter
        if status:
            base_query = base_query.filter(Alert.status.in_(status))
        
        # Severity filter
        if severity:
            base_query = base_query.filter(Alert.severity.in_(severity))
        
        # Source filter
        if source:
            base_query = base_query.filter(Alert.source.in_(source))
        
        # Service filter
        if service:
            base_query = base_query.filter(Alert.service.in_(service))
        
        # Time range filter
        if start_time:
            base_query = base_query.filter(Alert.created_at >= start_time)
        if end_time:
            base_query = base_query.filter(Alert.created_at <= end_time)
        
        # Tags filter
        if tags:
            for tag in tags:
                base_query = base_query.filter(
                    Alert.tags.op('?')(tag)
                )
        
        # Get total count
        total_count = base_query.count()
        
        # Apply sorting
        sort_column = getattr(Alert, sort_by, Alert.created_at)
        if sort_order.lower() == "desc":
            base_query = base_query.order_by(desc(sort_column))
        else:
            base_query = base_query.order_by(asc(sort_column))
        
        # Apply pagination
        alerts = base_query.offset(offset).limit(limit).all()
        
        return {
            "alerts": [self._alert_to_dict(alert) for alert in alerts],
            "total_count": total_count,
            "page": offset // limit + 1,
            "page_size": limit,
            "total_pages": (total_count + limit - 1) // limit
        }
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        # Status distribution
        status_stats = self.db.query(
            Alert.status,
            func.count(Alert.id).label('count')
        ).group_by(Alert.status).all()
        
        # Severity distribution
        severity_stats = self.db.query(
            Alert.severity,
            func.count(Alert.id).label('count')
        ).group_by(Alert.severity).all()
        
        # Alerts by time (last 24 hours)
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
        # Use database-agnostic datetime formatting
        hourly_stats = self.db.query(
            func.strftime('%Y-%m-%d %H:00:00', Alert.created_at).label('hour'),
            func.count(Alert.id).label('count')
        ).filter(
            Alert.created_at >= twenty_four_hours_ago
        ).group_by('hour').order_by('hour').all()
        
        # Top sources
        source_stats = self.db.query(
            Alert.source,
            func.count(Alert.id).label('count')
        ).group_by(Alert.source).order_by(desc(func.count(Alert.id))).limit(10).all()
        
        return {
            "status_distribution": [{"status": s.status, "count": s.count} for s in status_stats],
            "severity_distribution": [{"severity": s.severity, "count": s.count} for s in severity_stats],
            "hourly_trend": [{"hour": h.hour, "count": h.count} for h in hourly_stats],
            "top_sources": [{"source": s.source, "count": s.count} for s in source_stats],
            "total_alerts": self.db.query(Alert).count(),
            "active_alerts": self.db.query(Alert).filter(Alert.status == AlertStatus.ACTIVE).count()
        }
    
    def bulk_update_alerts(self, alert_ids: List[int], updates: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Validate alert IDs exist
            existing_alerts = self.db.query(Alert).filter(Alert.id.in_(alert_ids)).all()
            if len(existing_alerts) != len(alert_ids):
                return {"success": False, "error": "Some alert IDs not found"}
            
            # Apply updates
            update_count = self.db.query(Alert).filter(
                Alert.id.in_(alert_ids)
            ).update(updates, synchronize_session=False)
            
            self.db.commit()
            
            return {
                "success": True,
                "updated_count": update_count,
                "message": f"Successfully updated {update_count} alerts"
            }
        except Exception as e:
            self.db.rollback()
            return {"success": False, "error": str(e)}
    
    def export_alerts(self, alert_ids: List[int], format: str = "csv") -> Dict[str, Any]:
        alerts = self.db.query(Alert).filter(Alert.id.in_(alert_ids)).all()
        
        if format.lower() == "csv":
            # Convert to DataFrame
            data = [self._alert_to_dict(alert) for alert in alerts]
            df = pd.DataFrame(data)
            
            # Convert to CSV
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False)
            
            return {
                "success": True,
                "data": csv_buffer.getvalue(),
                "content_type": "text/csv",
                "filename": f"alerts_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        
        elif format.lower() == "json":
            data = [self._alert_to_dict(alert) for alert in alerts]
            return {
                "success": True,
                "data": json.dumps(data, indent=2, default=str),
                "content_type": "application/json",
                "filename": f"alerts_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            }
        
        else:
            return {"success": False, "error": "Unsupported export format"}
    
    def _alert_to_dict(self, alert: Alert) -> Dict[str, Any]:
        return {
            "id": alert.id,
            "title": alert.title,
            "description": alert.description,
            "severity": alert.severity,
            "status": alert.status,
            "source": alert.source,
            "service": alert.service,
            "environment": alert.environment,
            "tags": alert.tags,
            "metadata": alert.alert_metadata,
            "created_at": alert.created_at.isoformat() if alert.created_at else None,
            "updated_at": alert.updated_at.isoformat() if alert.updated_at else None,
            "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
            "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
            "acknowledged_by": alert.acknowledged_by
        }
