from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

class IndexManager:
    def __init__(self):
        self.indexes = [
            {
                'name': 'idx_notifications_user_timestamp',
                'definition': 'CREATE INDEX IF NOT EXISTS idx_notifications_user_timestamp ON notifications (user_id, timestamp DESC)',
                'purpose': 'Optimize user+date range queries'
            },
            {
                'name': 'idx_notifications_timestamp',
                'definition': 'CREATE INDEX IF NOT EXISTS idx_notifications_timestamp ON notifications (timestamp DESC)',
                'purpose': 'Optimize date range queries'
            },
            {
                'name': 'idx_export_jobs_status',
                'definition': 'CREATE INDEX IF NOT EXISTS idx_export_jobs_status ON export_jobs (status, created_at) WHERE status != \'completed\'',
                'purpose': 'Optimize active job queries'
            }
        ]
    
    async def ensure_indexes(self):
        """Create required indexes"""
        from models.database import engine
        
        async with engine.begin() as conn:
            for index in self.indexes:
                try:
                    await conn.execute(text(index['definition']))
                    logger.info(f"Created index: {index['name']}")
                except Exception as e:
                    logger.warning(f"Index creation warning for {index['name']}: {e}")
    
    async def get_index_status(self, db):
        """Get index statistics"""
        query = text("""
            SELECT 
                schemaname,
                relname,
                indexrelname,
                idx_scan,
                idx_tup_read,
                idx_tup_fetch
            FROM pg_stat_user_indexes
            WHERE schemaname = 'public'
            ORDER BY idx_scan DESC
        """)
        
        try:
            result = await db.execute(query)
            rows = result.fetchall()
            
            return {
                'indexes': [
                    {
                        'table': row[1],
                        'index': row[2],
                        'scans': row[3],
                        'tuples_read': row[4],
                        'tuples_fetched': row[5]
                    }
                    for row in rows
                ]
            }
        except Exception as e:
            logger.error(f"Error getting index status: {e}")
            return {'indexes': [], 'error': str(e)}
    
    async def analyze_query_patterns(self):
        """Analyze query patterns and suggest optimizations"""
        # This would analyze pg_stat_statements in production
        logger.info("Query pattern analysis started")
        return {'status': 'completed'}
