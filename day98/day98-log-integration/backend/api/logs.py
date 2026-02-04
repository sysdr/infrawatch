from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from typing import List, Optional
from datetime import datetime, timedelta
import json
import asyncio

from models.log_entry import LogEntry, LogQuery
from utils.redis_client import get_redis_client
from utils.elasticsearch_client import get_es_client
from workers.websocket_manager import WebSocketManager

router = APIRouter()
ws_manager = WebSocketManager()

@router.post("/", status_code=201)
async def ingest_log(log: LogEntry):
    """Ingest a new log entry into the pipeline"""
    redis = await get_redis_client()

    if not log.timestamp:
        log.timestamp = datetime.utcnow()

    stream_key = f"logs:{log.service}:{log.level}"
    await redis.xadd(
        stream_key,
        {
            "timestamp": log.timestamp.isoformat(),
            "level": log.level,
            "service": log.service,
            "message": log.message,
            "metadata": json.dumps(log.metadata or {})
        },
        maxlen=10000
    )

    await redis.lpush("index-queue", log.json())
    await redis.incr("metrics:logs:ingested")

    await ws_manager.broadcast(log.dict(), filters={
        "service": log.service,
        "level": log.level
    })

    return {"status": "ingested", "id": log.id}

@router.get("/search")
async def search_logs(
    query: Optional[str] = Query(None),
    service: Optional[str] = Query(None),
    level: Optional[str] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    limit: int = Query(100, le=1000)
):
    es = await get_es_client()

    must_clauses = []

    if query:
        must_clauses.append({
            "multi_match": {
                "query": query,
                "fields": ["message", "service"]
            }
        })

    if service:
        must_clauses.append({"term": {"service": service}})

    if level:
        must_clauses.append({"term": {"level": level}})

    if start_time or end_time:
        range_query = {}
        if start_time:
            range_query["gte"] = start_time.isoformat()
        if end_time:
            range_query["lte"] = end_time.isoformat()
        must_clauses.append({"range": {"timestamp": range_query}})

    search_start = datetime.utcnow()

    result = await es.search(
        index="logs-*",
        body={
            "query": {
                "bool": {"must": must_clauses}
            } if must_clauses else {"match_all": {}},
            "sort": [{"timestamp": "desc"}],
            "size": limit
        }
    )

    search_duration = (datetime.utcnow() - search_start).total_seconds()
    logs = [hit["_source"] for hit in result["hits"]["hits"]]

    return {
        "total": result["hits"]["total"]["value"],
        "logs": logs,
        "search_duration_ms": search_duration * 1000
    }

@router.websocket("/stream")
async def websocket_stream(websocket: WebSocket):
    await ws_manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "subscribe":
                filters = data.get("filters", {})
                await ws_manager.set_filters(websocket, filters)
                await websocket.send_json({
                    "type": "subscribed",
                    "filters": filters
                })
            elif data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket)

@router.get("/export")
async def export_logs(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    format: str = Query("json", regex="^(json|csv)$")
):
    days_old = (datetime.utcnow() - start_date).days

    if days_old <= 7:
        source = "elasticsearch"
        data = await _export_from_elasticsearch(start_date, end_date, format)
    elif days_old <= 30:
        source = "s3-athena"
        data = await _export_from_athena(start_date, end_date, format)
    else:
        source = "s3-glacier"
        data = await _request_glacier_restore(start_date, end_date)

    return {
        "source": source,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "format": format,
        "data": data
    }

async def _export_from_elasticsearch(start_date, end_date, format):
    return {"message": "Elasticsearch export (mock)"}

async def _export_from_athena(start_date, end_date, format):
    return {"message": "Athena export (mock)"}

async def _request_glacier_restore(start_date, end_date):
    return {"message": "Glacier restore requested, ETA 12 hours"}
