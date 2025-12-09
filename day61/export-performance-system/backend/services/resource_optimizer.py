from models.database import engine

class ResourceOptimizer:
    def __init__(self):
        self.pool_config = {
            'pool_size': 20,
            'max_overflow': 40,
            'pool_timeout': 30
        }
    
    async def get_pool_status(self):
        """Get database connection pool status"""
        pool = engine.pool
        
        return {
            'pool_size': pool.size(),
            'checked_in': pool.checkedin(),
            'checked_out': pool.checkedout(),
            'overflow': pool.overflow(),
            'total_connections': pool.size() + pool.overflow(),
            'utilization_percent': round((pool.checkedout() / (pool.size() + pool.overflow()) * 100), 2) if (pool.size() + pool.overflow()) > 0 else 0
        }
    
    def optimize_batch_size(self, total_records: int, available_memory_mb: int) -> int:
        """Calculate optimal batch size based on available resources"""
        # Estimate 1KB per record
        max_batch_by_memory = (available_memory_mb * 1024) // 1
        
        # Cap at 10,000 records per batch
        optimal_batch = min(max_batch_by_memory, 10000)
        
        return max(optimal_batch, 1000)  # Minimum 1000
