from datetime import datetime, timedelta
from collections import deque
import statistics

class PerformanceMonitor:
    def __init__(self):
        self.query_times = deque(maxlen=1000)
        self.export_metrics = {
            'total_exports': 0,
            'cached_exports': 0,
            'slow_queries': []
        }
        self.all_queries = deque(maxlen=100)  # Track all recent queries
        self.slow_query_threshold_ms = 500
    
    async def track_export(self, query_time: float, total_time: float, row_count: int, cached: bool):
        """Track export performance metrics"""
        query_time_ms = query_time * 1000
        
        self.query_times.append(query_time_ms)
        self.export_metrics['total_exports'] += 1
        
        if cached:
            self.export_metrics['cached_exports'] += 1
        
        # Track all queries (for display purposes)
        query_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'query_time_ms': round(query_time_ms, 2),
            'total_time_ms': round(total_time * 1000, 2),
            'row_count': row_count,
            'cached': cached,
            'is_slow': query_time_ms > self.slow_query_threshold_ms
        }
        self.all_queries.append(query_record)
        
        # Track slow queries separately
        if query_time_ms > self.slow_query_threshold_ms:
            self.export_metrics['slow_queries'].append(query_record)
            
            # Keep only last 100 slow queries
            if len(self.export_metrics['slow_queries']) > 100:
                self.export_metrics['slow_queries'] = self.export_metrics['slow_queries'][-100:]
    
    async def get_metrics(self):
        """Get performance statistics"""
        if not self.query_times:
            return {
                'query_times': {'p50': 0, 'p95': 0, 'p99': 0, 'avg': 0},
                'exports': self.export_metrics
            }
        
        times = list(self.query_times)
        times.sort()
        
        p50_idx = int(len(times) * 0.50)
        p95_idx = int(len(times) * 0.95)
        p99_idx = int(len(times) * 0.99)
        
        cache_rate = 0
        if self.export_metrics['total_exports'] > 0:
            cache_rate = (self.export_metrics['cached_exports'] / 
                         self.export_metrics['total_exports'] * 100)
        
        return {
            'query_times': {
                'p50_ms': round(times[p50_idx], 2) if times else 0,
                'p95_ms': round(times[p95_idx], 2) if times else 0,
                'p99_ms': round(times[p99_idx], 2) if times else 0,
                'avg_ms': round(statistics.mean(times), 2) if times else 0,
                'min_ms': round(min(times), 2) if times else 0,
                'max_ms': round(max(times), 2) if times else 0
            },
            'exports': {
                'total': self.export_metrics['total_exports'],
                'cached': self.export_metrics['cached_exports'],
                'cache_hit_rate_percent': round(cache_rate, 2),
                'slow_query_count': len(self.export_metrics['slow_queries'])
            }
        }
    
    async def get_slow_queries(self):
        """Get slow query log - returns slow queries if any, otherwise recent queries"""
        slow_queries = self.export_metrics['slow_queries'][-50:]  # Last 50 slow queries
        
        # If no slow queries, return recent queries (last 20) so user sees activity
        if not slow_queries:
            recent_queries = list(self.all_queries)[-20:]  # Last 20 queries
            return {
                'threshold_ms': self.slow_query_threshold_ms,
                'queries': recent_queries,
                'note': 'Showing recent queries (no slow queries yet)'
            }
        
        return {
            'threshold_ms': self.slow_query_threshold_ms,
            'queries': slow_queries
        }
