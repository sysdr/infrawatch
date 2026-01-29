from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.search_service import get_search_service
from app.services.websocket_manager import ws_manager
from typing import Optional
import uuid

router = APIRouter()

@router.get("/search")
async def search_logs(
    q: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    user_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Search logs with query language"""
    search_service = get_search_service(db)
    return search_service.search(q, page, page_size, user_id)

@router.get("/suggestions")
async def get_suggestions(
    q: str = Query(..., description="Partial query"),
    db: Session = Depends(get_db)
):
    """Get query suggestions"""
    search_service = get_search_service(db)
    return {"suggestions": search_service.get_suggestions(q)}

@router.get("/facets")
async def get_facets(
    q: str = Query("", description="Search query"),
    db: Session = Depends(get_db)
):
    """Get faceted search results"""
    search_service = get_search_service(db)
    return search_service.get_facets(q)

@router.websocket("/ws/search")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time search"""
    client_id = str(uuid.uuid4())
    await ws_manager.connect(websocket, client_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "subscribe":
                query = data.get("query", "")
                await ws_manager.subscribe_to_search(client_id, query)
                await websocket.send_json({
                    "type": "subscribed",
                    "query": query
                })
            
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, client_id)

@router.get("/analytics")
async def get_analytics(db: Session = Depends(get_db)):
    """Get search analytics"""
    from sqlalchemy import select, func
    from app.models.log import SearchQuery
    
    # Most common queries
    common_queries = db.execute(
        select(SearchQuery.query_string, func.count(SearchQuery.id).label('count'))
        .group_by(SearchQuery.query_string)
        .order_by(func.count(SearchQuery.id).desc())
        .limit(10)
    ).all()
    
    # Average execution time
    avg_time = db.execute(
        select(func.avg(SearchQuery.execution_time_ms))
    ).scalar()
    
    # Cache hit rate
    total_queries = db.execute(select(func.count(SearchQuery.id))).scalar()
    cache_hits = db.execute(
        select(func.count(SearchQuery.id))
        .where(SearchQuery.cache_hit == 'HIT')
    ).scalar()
    total_queries = int(total_queries) if total_queries is not None else 0
    cache_hits = int(cache_hits) if cache_hits is not None else 0

    return {
        "common_queries": [{"query": q, "count": int(c)} for q, c in common_queries],
        "avg_execution_time_ms": float(avg_time) if avg_time is not None else 0.0,
        "cache_hit_rate": (cache_hits / total_queries) if total_queries > 0 else 0.0,
        "total_queries": total_queries,
    }
