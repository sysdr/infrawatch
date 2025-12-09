from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import json
import time
import psutil
import logging
from prometheus_client import Counter, Histogram, Gauge, generate_latest

from models.database import init_db, get_db, close_db
from services.query_optimizer import QueryOptimizer
from services.cache_manager import CacheManager
from services.performance_monitor import PerformanceMonitor
from services.index_manager import IndexManager
from services.resource_optimizer import ResourceOptimizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
export_requests = Counter('export_requests_total', 'Total export requests', ['status'])
export_duration = Histogram('export_duration_seconds', 'Export duration')
cache_hits = Counter('cache_hits_total', 'Cache hits', ['tier'])
query_duration = Histogram('query_duration_seconds', 'Query execution time')
active_exports = Gauge('active_exports', 'Currently active exports')

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    await app.state.cache_manager.connect()
    await app.state.index_manager.ensure_indexes()
    logger.info("Export Performance System started")
    yield
    # Shutdown
    await app.state.cache_manager.close()
    await close_db()
    logger.info("Export Performance System stopped")

app = FastAPI(title="Export Performance System", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
app.state.query_optimizer = QueryOptimizer()
app.state.cache_manager = CacheManager()
app.state.performance_monitor = PerformanceMonitor()
app.state.index_manager = IndexManager()
app.state.resource_optimizer = ResourceOptimizer()

@app.get("/")
async def root():
    return {
        "service": "Export Performance System",
        "version": "1.0.0",
        "status": "operational"
    }

@app.post("/api/exports/notifications")
async def export_notifications(
    user_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    format: str = "json",
    use_cache: bool = True
):
    """Export notifications with performance optimization"""
    start_time = time.time()
    active_exports.inc()
    
    try:
        # Generate cache key
        cache_key = f"export:notifications:{user_id}:{start_date}:{end_date}:{format}"
        
        # Check cache first
        if use_cache:
            cached_result = await app.state.cache_manager.get(cache_key)
            if cached_result:
                cache_hits.labels(tier='redis').inc()
                export_requests.labels(status='success').inc()
                duration = time.time() - start_time
                export_duration.observe(duration)
                
                # Track cached query performance
                data = json.loads(cached_result)
                await app.state.performance_monitor.track_export(
                    query_time=0,  # No database query for cached results
                    total_time=duration,
                    row_count=len(data),
                    cached=True
                )
                
                return {
                    "data": data,
                    "source": "cache",
                    "execution_time_ms": round(duration * 1000, 2),
                    "cached": True
                }
        
        # Optimize and execute query
        query_start = time.time()
        optimized_query = app.state.query_optimizer.optimize_export_query(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        async with get_db() as db:
            result = await db.execute(optimized_query)
            rows = result.fetchall()
        
        query_duration.observe(time.time() - query_start)
        
        # Format results
        data = [
            {
                "id": row[0],
                "user_id": row[1],
                "type": row[2],
                "status": row[3],
                "timestamp": row[4].isoformat() if row[4] else None,
                "metadata": row[5]
            }
            for row in rows
        ]
        
        # Cache results
        if use_cache:
            await app.state.cache_manager.set(
                cache_key,
                json.dumps(data),
                ttl=900  # 15 minutes
            )
        
        export_requests.labels(status='success').inc()
        duration = time.time() - start_time
        export_duration.observe(duration)
        
        # Track performance
        await app.state.performance_monitor.track_export(
            query_time=time.time() - query_start,
            total_time=duration,
            row_count=len(data),
            cached=False
        )
        
        return {
            "data": data,
            "source": "database",
            "execution_time_ms": round(duration * 1000, 2),
            "row_count": len(data),
            "cached": False
        }
        
    except Exception as e:
        export_requests.labels(status='error').inc()
        logger.error(f"Export error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        active_exports.dec()

@app.get("/api/performance/metrics")
async def get_performance_metrics():
    """Get real-time performance metrics"""
    metrics = await app.state.performance_monitor.get_metrics()
    
    # Add system metrics
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    
    metrics.update({
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_used_mb": memory.used / 1024 / 1024
        }
    })
    
    return metrics

@app.get("/api/performance/slow-queries")
async def get_slow_queries():
    """Get slow query log"""
    return await app.state.performance_monitor.get_slow_queries()

@app.get("/api/cache/stats")
async def get_cache_stats():
    """Get cache statistics"""
    return await app.state.cache_manager.get_stats()

@app.post("/api/cache/invalidate")
async def invalidate_cache(pattern: str = "*"):
    """Invalidate cache by pattern"""
    count = await app.state.cache_manager.invalidate(pattern)
    return {"invalidated": count, "pattern": pattern}

@app.get("/api/indexes/status")
async def get_index_status():
    """Get database index status"""
    async with get_db() as db:
        return await app.state.index_manager.get_index_status(db)

@app.post("/api/indexes/analyze")
async def analyze_indexes(background_tasks: BackgroundTasks):
    """Analyze and recommend indexes"""
    background_tasks.add_task(app.state.index_manager.analyze_query_patterns)
    return {"status": "analysis_started"}

@app.get("/api/resources/pool-status")
async def get_pool_status():
    """Get database connection pool status"""
    return await app.state.resource_optimizer.get_pool_status()

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
