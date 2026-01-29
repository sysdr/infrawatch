from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc
from app.models.log import Log, SearchQuery
from app.services.query_parser import parser
from app.services.sql_translator import sql_translator
from app.core.database import get_redis
from typing import List, Dict, Any, Optional
import json
import hashlib
import time
from datetime import datetime

class SearchService:
    def __init__(self, db: Session):
        self.db = db
        self.redis = get_redis()
        self.cache_ttl = 60
    
    def search(
        self, 
        query_string: str, 
        page: int = 1, 
        page_size: int = 50,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute search query with caching"""
        start_time = time.time()
        
        # Check cache
        cache_key = self._generate_cache_key(query_string, page, page_size)
        cached_result = self.redis.get(cache_key)
        
        if cached_result:
            result = json.loads(cached_result)
            self._log_query(query_string, user_id, int((time.time() - start_time) * 1000), 
                          result["total"], "HIT")
            return result
        
        # Parse query
        ast = parser.parse(query_string)
        
        # Build SQL query
        base_query = select(Log).order_by(desc(Log.timestamp))
        query, params = sql_translator.translate(ast, base_query)
        
        # Get total count
        count_query = select(func.count()).select_from(Log)
        count_query, _ = sql_translator.translate(ast, count_query)
        total = self.db.execute(count_query).scalar()
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        # Execute
        logs = self.db.execute(query).scalars().all()
        
        # Format result
        result = {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
            "logs": [self._format_log(log) for log in logs],
            "query_info": {
                "original": query_string,
                "ast": ast
            }
        }
        
        # Cache result
        self.redis.setex(cache_key, self.cache_ttl, json.dumps(result, default=str))
        
        # Log query
        execution_time = int((time.time() - start_time) * 1000)
        self._log_query(query_string, user_id, execution_time, total, "MISS")
        
        return result
    
    def get_suggestions(self, partial_query: str) -> List[str]:
        """Get query suggestions based on common fields and values"""
        suggestions = []
        
        # Field suggestions
        if ':' not in partial_query:
            fields = ['level:', 'service:', 'user_id:', 'timestamp:', 'message:']
            suggestions.extend([f for f in fields if f.startswith(partial_query.lower())])
        else:
            # Value suggestions
            field = partial_query.split(':')[0]
            if field in ['level', 'service']:
                column = getattr(Log, field, None)
                if column:
                    values = self.db.execute(
                        select(column).distinct().limit(10)
                    ).scalars().all()
                    suggestions.extend([f"{field}:{v}" for v in values])
        
        return suggestions[:10]
    
    def get_facets(self, query_string: str) -> Dict[str, Any]:
        """Get faceted search results"""
        ast = parser.parse(query_string)
        
        base_query = select(Log)
        query, _ = sql_translator.translate(ast, base_query)
        
        # Service facets
        service_facets = self.db.execute(
            select(Log.service, func.count(Log.id).label('count'))
            .select_from(query.subquery())
            .group_by(Log.service)
            .order_by(desc('count'))
            .limit(10)
        ).all()
        
        # Level facets
        level_facets = self.db.execute(
            select(Log.level, func.count(Log.id).label('count'))
            .select_from(query.subquery())
            .group_by(Log.level)
            .order_by(desc('count'))
        ).all()
        
        # Time facets (hourly)
        time_facets = self.db.execute(
            select(
                func.date_trunc('hour', Log.timestamp).label('hour'),
                func.count(Log.id).label('count')
            )
            .select_from(query.subquery())
            .group_by('hour')
            .order_by(desc('hour'))
            .limit(24)
        ).all()
        
        return {
            "services": [{"value": s, "count": c} for s, c in service_facets],
            "levels": [{"value": l, "count": c} for l, c in level_facets],
            "timeline": [{"time": str(t), "count": c} for t, c in time_facets]
        }
    
    def _generate_cache_key(self, query: str, page: int, page_size: int) -> str:
        """Generate cache key from query parameters"""
        key_data = f"{query}:{page}:{page_size}"
        return f"search:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    def _format_log(self, log: Log) -> Dict[str, Any]:
        """Format log object for API response"""
        return {
            "id": log.id,
            "timestamp": log.timestamp.isoformat(),
            "level": log.level,
            "service": log.service,
            "message": log.message,
            "user_id": log.user_id,
            "request_id": log.request_id,
            # underlying column is still named 'metadata', but attribute is metadata_json
            "metadata": getattr(log, "metadata_json", None),
        }
    
    def _log_query(self, query: str, user_id: Optional[str], execution_time: int, 
                   result_count: int, cache_status: str):
        """Log search query for analytics"""
        search_query = SearchQuery(
            query_string=query,
            user_id=user_id or "anonymous",
            execution_time_ms=execution_time,
            result_count=result_count,
            cache_hit=cache_status
        )
        self.db.add(search_query)
        self.db.commit()

def get_search_service(db: Session) -> SearchService:
    return SearchService(db)
