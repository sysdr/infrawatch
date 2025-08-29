from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import io
import csv
import json

from config.database import get_db
from app.models.schemas import (
    MetricQueryRequest, MetricQueryResponse, ExportRequest, 
    AggregationType, IntervalType, ExportFormat
)
from app.services.metrics_service import metrics_service
import structlog

logger = structlog.get_logger()
router = APIRouter(prefix="/api/v1/metrics", tags=["metrics"])

@router.get("/query", response_model=MetricQueryResponse)
async def query_metrics(
    metric_name: str = Query(..., description="Name of the metric"),
    start_time: datetime = Query(..., description="Start time (ISO format)"),
    end_time: datetime = Query(..., description="End time (ISO format)"),
    interval: IntervalType = Query(default=IntervalType.five_minutes),
    aggregations: List[AggregationType] = Query(default=[AggregationType.avg]),
    limit: int = Query(default=1000, ge=1, le=10000),
    db: Session = Depends(get_db)
):
    """Query metrics with time range filtering and aggregation"""
    
    try:
        request = MetricQueryRequest(
            metric_name=metric_name,
            start_time=start_time,
            end_time=end_time,
            interval=interval,
            aggregations=aggregations,
            limit=limit
        )
        
        result = await metrics_service.query_metrics(db, request)
        
        logger.info(
            "Metrics query completed",
            metric_name=metric_name,
            data_points=result.total_points,
            cache_hit=result.cache_hit
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Query error", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/export")
async def export_metrics(
    metric_name: str = Query(..., description="Name of the metric"),
    start_time: datetime = Query(..., description="Start time"),
    end_time: datetime = Query(..., description="End time"),
    format: ExportFormat = Query(default=ExportFormat.json),
    aggregation: AggregationType = Query(default=AggregationType.avg),
    interval: IntervalType = Query(default=IntervalType.five_minutes),
    db: Session = Depends(get_db)
):
    """Export metrics data in JSON or CSV format"""
    
    try:
        request = ExportRequest(
            metric_name=metric_name,
            start_time=start_time,
            end_time=end_time,
            format=format,
            aggregation=aggregation,
            interval=interval
        )
        
        export_data = await metrics_service.export_metrics(db, request)
        
        if format == ExportFormat.json:
            return export_data
        
        elif format == ExportFormat.csv:
            # Generate CSV
            output = io.StringIO()
            writer = csv.DictWriter(
                output, 
                fieldnames=['timestamp', 'metric_name', 'value', 'aggregation']
            )
            writer.writeheader()
            writer.writerows(export_data['data'])
            
            csv_content = output.getvalue()
            output.close()
            
            filename = f"{metric_name}_{start_time.strftime('%Y%m%d')}_{end_time.strftime('%Y%m%d')}.csv"
            
            return StreamingResponse(
                io.StringIO(csv_content),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
    
    except Exception as e:
        logger.error("Export error", error=str(e))
        raise HTTPException(status_code=500, detail="Export failed")

@router.get("/list")
async def list_available_metrics(
    db: Session = Depends(get_db),
    limit: int = Query(default=100, ge=1, le=1000)
):
    """List all available metric names"""
    
    try:
        from app.models.metric import Metric
        from sqlalchemy import distinct
        
        result = db.query(distinct(Metric.name)).limit(limit).all()
        metric_names = [row[0] for row in result]
        
        return {
            "metrics": metric_names,
            "count": len(metric_names)
        }
        
    except Exception as e:
        logger.error("List metrics error", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list metrics")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    
    try:
        from config.database import get_redis
        
        # Test database connection
        db = next(get_db())
        db.execute("SELECT 1")
        db_status = "healthy"
        
        # Test Redis connection
        try:
            redis_client = await get_redis()
            await redis_client.ping()
            cache_status = "healthy"
        except:
            cache_status = "unhealthy"
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "database": db_status,
            "cache": cache_status,
            "version": "1.0.0"
        }
        
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow(),
            "error": str(e)
        }
