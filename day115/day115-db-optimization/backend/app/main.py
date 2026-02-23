import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import text
import threading
import time

from .config import settings
from .database import router
from .optimizer import (
    get_slow_queries, get_index_health, get_table_bloat,
    explain_query, get_missing_index_suggestions
)
from .partitions import get_partition_stats, test_partition_pruning
from .replication import get_replication_status, get_connection_stats

app = FastAPI(title="DB Optimization API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Background lag poller
def lag_poller():
    while True:
        try:
            router.update_replication_lag()
        except Exception:
            pass
        time.sleep(2)

threading.Thread(target=lag_poller, daemon=True).start()

# ── Query Analysis ──────────────────────────────────────────────────────────
@app.get("/api/queries/slow")
def slow_queries(limit: int = 20):
    return get_slow_queries(limit)

@app.get("/api/queries/explain/{query_id}")
def explain(query_id: str):
    result = explain_query(query_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Query ID not found")
    return result

@app.get("/api/queries/suggestions")
def index_suggestions():
    return get_missing_index_suggestions()

# ── Index Management ────────────────────────────────────────────────────────
@app.get("/api/indexes/health")
def index_health():
    return get_index_health()

class IndexCreateRequest(BaseModel):
    table_name: str
    columns: list[str]
    index_type: str = "btree"
    unique: bool = False

@app.post("/api/indexes/create")
def create_index(req: IndexCreateRequest):
    # Sanitize: allow only alphanumeric and underscore
    import re
    for name in [req.table_name] + req.columns:
        if not re.match(r'^[a-zA-Z0-9_]+$', name):
            raise HTTPException(status_code=400, detail=f"Invalid identifier: {name}")
    cols = ", ".join(req.columns)
    idx_name = f"idx_{req.table_name}_{'_'.join(req.columns)}"
    unique_kw = "UNIQUE" if req.unique else ""
    ddl = f"CREATE {unique_kw} INDEX CONCURRENTLY IF NOT EXISTS {idx_name} ON {req.table_name} USING {req.index_type} ({cols})"
    try:
        # CONCURRENTLY cannot run inside a transaction - use autocommit
        with router.get_write_engine().connect().execution_options(
            isolation_level="AUTOCOMMIT"
        ) as conn:
            conn.execute(text(ddl))
        return {"status": "created", "index_name": idx_name, "ddl": ddl}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Partition Stats ─────────────────────────────────────────────────────────
@app.get("/api/partitions/stats")
def partition_stats():
    return get_partition_stats()

@app.get("/api/partitions/pruning-test")
def pruning_test(start: str = "2025-05-01", end: str = "2025-06-01"):
    return test_partition_pruning(start, end)

# ── Replication ─────────────────────────────────────────────────────────────
@app.get("/api/replication/status")
def replication_status():
    return get_replication_status()

@app.get("/api/replication/connections")
def connection_stats():
    return get_connection_stats()

# ── Maintenance ─────────────────────────────────────────────────────────────
class VacuumRequest(BaseModel):
    table_name: str
    analyze: bool = True

@app.post("/api/maintenance/vacuum")
def run_vacuum(req: VacuumRequest):
    import re
    if not re.match(r'^[a-zA-Z0-9_]+$', req.table_name):
        raise HTTPException(status_code=400, detail="Invalid table name")
    cmd = f"VACUUM {'ANALYZE' if req.analyze else ''} {req.table_name}"
    try:
        with router.get_write_engine().connect().execution_options(
            isolation_level="AUTOCOMMIT"
        ) as conn:
            conn.execute(text(cmd))
        return {"status": "completed", "command": cmd}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/maintenance/analyze")
def run_analyze():
    try:
        with router.get_write_engine().connect().execution_options(
            isolation_level="AUTOCOMMIT"
        ) as conn:
            conn.execute(text("ANALYZE"))
        return {"status": "completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/maintenance/bloat")
def table_bloat():
    return get_table_bloat()

# ── Dashboard Summary ───────────────────────────────────────────────────────
@app.get("/api/dashboard/summary")
def dashboard_summary():
    """Single call for dashboard initial load."""
    slow = get_slow_queries(5)
    repl = get_replication_status()
    conns = get_connection_stats()
    bloat = get_table_bloat()
    avg_latency = sum(q['avg_ms'] for q in slow) / len(slow) if slow else 0
    unhealthy = sum(1 for b in bloat if b['bloat_pct'] > 10)
    return {
        "avg_query_latency_ms": round(avg_latency, 2),
        "slow_query_count": len(slow),
        "replica_lag_ms": repl["current_router_lag_ms"],
        "connection_utilization_pct": conns["utilization_pct"],
        "tables_needing_vacuum": unhealthy,
        "routing_to_replica": repl["routing_to_replica"]
    }

@app.get("/health")
def health():
    try:
        with router.primary_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "db": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
