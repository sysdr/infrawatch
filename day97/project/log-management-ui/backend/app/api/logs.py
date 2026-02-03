"""Logs API routes."""
import json
from pathlib import Path

from fastapi import APIRouter, Query

router = APIRouter()

DEMO_LOGS = Path(__file__).resolve().parents[2] / "data" / "demo_logs.json"


@router.get("/logs/search")
def search_logs(
    q: str = Query("*", description="Search query"),
    limit: int = Query(20, ge=1, le=100),
):
    """Search logs. Uses DB if available, else demo_logs.json."""
    try:
        from backend.app.services.search import search_logs as do_search
        result = do_search(q, limit=limit)
        return {"logs": result}
    except Exception:
        pass
    # Fallback: read from demo_logs.json
    if DEMO_LOGS.exists():
        with open(DEMO_LOGS) as f:
            logs = json.load(f)
        return {"logs": logs[:limit]}
    return {"logs": [], "items": []}
