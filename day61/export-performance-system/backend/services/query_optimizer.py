from sqlalchemy import text, select
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class QueryOptimizer:
    def __init__(self):
        self.optimization_rules = {
            'use_index': True,
            'limit_default': 10000,
            'enable_parallel': True
        }
    
    def optimize_export_query(self, user_id=None, start_date=None, end_date=None):
        """Generate optimized query with proper indexing hints"""
        
        # Base query with index hints
        query_parts = ["SELECT id, user_id, type, status, timestamp, metadata FROM notifications"]
        where_clauses = []
        
        # Add filters with indexed columns first
        if user_id:
            where_clauses.append(f"user_id = '{user_id}'")
        
        if start_date:
            where_clauses.append(f"timestamp >= '{start_date}'")
        
        if end_date:
            where_clauses.append(f"timestamp <= '{end_date}'")
        
        if where_clauses:
            query_parts.append("WHERE " + " AND ".join(where_clauses))
        
        # Order by indexed column
        query_parts.append("ORDER BY timestamp DESC")
        
        # Add limit to prevent runaway queries
        query_parts.append(f"LIMIT {self.optimization_rules['limit_default']}")
        
        query = " ".join(query_parts)
        logger.info(f"Optimized query: {query}")
        
        return text(query)
    
    def analyze_query_plan(self, query):
        """Analyze query execution plan"""
        explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"
        return explain_query
    
    def suggest_indexes(self, slow_queries):
        """Suggest indexes based on slow query patterns"""
        suggestions = []
        
        for query in slow_queries:
            if "user_id" in query and "timestamp" in query:
                suggestions.append({
                    "index": "idx_user_timestamp",
                    "definition": "CREATE INDEX idx_user_timestamp ON notifications (user_id, timestamp DESC)",
                    "reason": "Optimizes user+date range queries"
                })
        
        return suggestions
