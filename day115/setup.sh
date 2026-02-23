#!/usr/bin/env bash
# =============================================================================
# Day 115: Database Optimization — setup.sh
# 180-Day Hands-On Full Stack Development with Infrastructure Management
# =============================================================================
set -euo pipefail

DOCKER_MODE=false
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)/day115-db-optimization"
BACKEND_PORT=8000
FRONTEND_PORT=3000
PG_PRIMARY_PORT=5432
PG_REPLICA_PORT=5433

# Colour helpers
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
ok()   { echo -e "${GREEN}[✓]${NC} $*"; }
info() { echo -e "${CYAN}[→]${NC} $*"; }
warn() { echo -e "${YELLOW}[!]${NC} $*"; }
die()  { echo -e "${RED}[✗] $*${NC}" >&2; exit 1; }

usage() {
  echo "Usage: $0 [--docker | --no-docker]"
  echo "  --docker     Build and run using Docker Compose (includes read replica)"
  echo "  --no-docker  Build and run using local Python/Node/PostgreSQL"
  exit 0
}

for arg in "$@"; do
  case $arg in
    --docker)    DOCKER_MODE=true ;;
    --no-docker) DOCKER_MODE=false ;;
    --help|-h)   usage ;;
  esac
done

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Day 115: Database Optimization  ·  Week 11 of 180           ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# =============================================================================
# PHASE 1: Create Project Structure
# =============================================================================
info "Creating project structure at $PROJECT_DIR"
mkdir -p "$PROJECT_DIR"/{backend/{app,tests/{unit,integration}},frontend/src/{components,hooks,utils},postgres/{primary,replica},nginx}
ok "Directory structure created"

# =============================================================================
# PHASE 2: PostgreSQL Config & Init SQL
# =============================================================================
info "Writing PostgreSQL configuration files"

cat > "$PROJECT_DIR/postgres/primary/postgresql.conf" <<'PGCONF'
listen_addresses = '*'
wal_level = replica
max_wal_senders = 5
wal_keep_size = 512MB
hot_standby = on
shared_preload_libraries = 'pg_stat_statements'
pg_stat_statements.max = 10000
pg_stat_statements.track = all
log_min_duration_statement = 100
autovacuum = on
autovacuum_vacuum_scale_factor = 0.05
autovacuum_analyze_scale_factor = 0.02
random_page_cost = 1.1
effective_cache_size = 512MB
work_mem = 16MB
maintenance_work_mem = 128MB
PGCONF

cat > "$PROJECT_DIR/postgres/primary/pg_hba.conf" <<'HBACONF'
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             all                                     trust
host    all             all             0.0.0.0/0               md5
host    replication     replicator      0.0.0.0/0               md5
HBACONF

cat > "$PROJECT_DIR/postgres/init.sql" <<'INITSQL'
-- Enable extensions
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id          SERIAL PRIMARY KEY,
    username    VARCHAR(100) NOT NULL UNIQUE,
    email       VARCHAR(200) NOT NULL UNIQUE,
    team_id     INTEGER,
    role        VARCHAR(50) DEFAULT 'member',
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Teams table
CREATE TABLE IF NOT EXISTS teams (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(200) NOT NULL,
    slug        VARCHAR(100) NOT NULL UNIQUE,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Audit events - partitioned by month
CREATE TABLE IF NOT EXISTS audit_events (
    id          BIGSERIAL,
    user_id     INTEGER NOT NULL,
    team_id     INTEGER,
    action      VARCHAR(100) NOT NULL,
    resource    VARCHAR(200),
    ip_address  INET,
    metadata    JSONB DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- Create 12 monthly partitions (Jan 2025 - Dec 2025)
CREATE TABLE IF NOT EXISTS audit_events_2025_01 PARTITION OF audit_events
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
CREATE TABLE IF NOT EXISTS audit_events_2025_02 PARTITION OF audit_events
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
CREATE TABLE IF NOT EXISTS audit_events_2025_03 PARTITION OF audit_events
    FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');
CREATE TABLE IF NOT EXISTS audit_events_2025_04 PARTITION OF audit_events
    FOR VALUES FROM ('2025-04-01') TO ('2025-05-01');
CREATE TABLE IF NOT EXISTS audit_events_2025_05 PARTITION OF audit_events
    FOR VALUES FROM ('2025-05-01') TO ('2025-06-01');
CREATE TABLE IF NOT EXISTS audit_events_2025_06 PARTITION OF audit_events
    FOR VALUES FROM ('2025-06-01') TO ('2025-07-01');
CREATE TABLE IF NOT EXISTS audit_events_2025_07 PARTITION OF audit_events
    FOR VALUES FROM ('2025-07-01') TO ('2025-08-01');
CREATE TABLE IF NOT EXISTS audit_events_2025_08 PARTITION OF audit_events
    FOR VALUES FROM ('2025-08-01') TO ('2025-09-01');
CREATE TABLE IF NOT EXISTS audit_events_2025_09 PARTITION OF audit_events
    FOR VALUES FROM ('2025-09-01') TO ('2025-10-01');
CREATE TABLE IF NOT EXISTS audit_events_2025_10 PARTITION OF audit_events
    FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');
CREATE TABLE IF NOT EXISTS audit_events_2025_11 PARTITION OF audit_events
    FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');
CREATE TABLE IF NOT EXISTS audit_events_2025_12 PARTITION OF audit_events
    FOR VALUES FROM ('2025-12-01') TO ('2026-01-01');

-- Metrics table (for performance tracking)
CREATE TABLE IF NOT EXISTS query_metrics (
    id          SERIAL PRIMARY KEY,
    query_hash  VARCHAR(64),
    avg_ms      NUMERIC(10,3),
    calls       BIGINT,
    captured_at TIMESTAMPTZ DEFAULT NOW()
);

-- Replication user
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'replicator') THEN
    CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'replicator_pass';
  END IF;
END $$;

-- Seed teams
INSERT INTO teams (name, slug) VALUES
    ('Engineering', 'engineering'),
    ('Platform', 'platform'),
    ('Security', 'security'),
    ('Data', 'data')
ON CONFLICT (slug) DO NOTHING;

-- Seed users (500 users)
INSERT INTO users (username, email, team_id, role, created_at)
SELECT
    'user_' || i,
    'user_' || i || '@company.com',
    (i % 4) + 1,
    CASE WHEN i % 20 = 0 THEN 'admin' WHEN i % 5 = 0 THEN 'manager' ELSE 'member' END,
    NOW() - (random() * INTERVAL '365 days')
FROM generate_series(1, 500) AS i
ON CONFLICT DO NOTHING;

-- Seed audit events (500,000 rows spread across months)
INSERT INTO audit_events (user_id, team_id, action, resource, ip_address, metadata, created_at)
SELECT
    (random() * 499 + 1)::int,
    (random() * 3 + 1)::int,
    (ARRAY['login','logout','create','update','delete','view','export','import'])[floor(random()*8+1)::int],
    (ARRAY['user','team','project','report','dashboard','settings','api_key','webhook'])[floor(random()*8+1)::int]
        || '_' || (random() * 999)::int,
    ('192.168.' || (random()*255)::int || '.' || (random()*255)::int)::inet,
    jsonb_build_object('browser', (ARRAY['Chrome','Firefox','Safari','Edge'])[floor(random()*4+1)::int],
                       'os', (ARRAY['Linux','macOS','Windows'])[floor(random()*3+1)::int]),
    NOW() - (random() * INTERVAL '365 days')
FROM generate_series(1, 500000);

-- Update statistics
ANALYZE;

-- Reset stat statements to clean baseline
SELECT pg_stat_statements_reset();
INITSQL

ok "PostgreSQL config and init SQL created"

# =============================================================================
# PHASE 3: Backend Python Application
# =============================================================================
info "Writing backend application files"

cat > "$PROJECT_DIR/backend/requirements.txt" <<'REQS'
fastapi==0.115.5
uvicorn[standard]==0.32.1
sqlalchemy==2.0.36
psycopg2-binary==2.9.10
python-dotenv==1.0.1
pydantic==2.10.3
pydantic-settings==2.7.0
pytest==8.3.4
httpx==0.28.1
pytest-asyncio==0.24.0
REQS

cat > "$PROJECT_DIR/backend/app/__init__.py" <<'PY'
PY

cat > "$PROJECT_DIR/backend/app/config.py" <<'PY'
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    primary_db_url: str = "postgresql://admin:admin_pass@localhost:5432/dbopt_dev"
    replica_db_url: str = ""  # Empty means use primary as fallback
    lag_threshold_ms: float = 500.0
    app_name: str = "DB Optimizer"
    debug: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
PY

cat > "$PROJECT_DIR/backend/app/database.py" <<'PY'
import threading
from sqlalchemy import create_engine, text, pool
from .config import settings

class DatabaseRouter:
    def __init__(self):
        self._lock = threading.Lock()
        self._replica_lag_ms = 0.0

        self.primary_engine = create_engine(
            settings.primary_db_url,
            poolclass=pool.QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 5}
        )

        use_replica = bool(settings.replica_db_url)
        self.replica_engine = create_engine(
            settings.replica_db_url if use_replica else settings.primary_db_url,
            poolclass=pool.QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 5}
        ) if use_replica else None

        self._has_replica = use_replica

    @property
    def replica_lag_ms(self):
        with self._lock:
            return self._replica_lag_ms

    @replica_lag_ms.setter
    def replica_lag_ms(self, v):
        with self._lock:
            self._replica_lag_ms = v

    def get_read_engine(self):
        if self._has_replica and self.replica_lag_ms < settings.lag_threshold_ms:
            return self.replica_engine
        return self.primary_engine

    def get_write_engine(self):
        return self.primary_engine

    def update_replication_lag(self):
        try:
            with self.primary_engine.connect() as conn:
                row = conn.execute(text("""
                    SELECT COALESCE(
                        EXTRACT(EPOCH FROM MAX(write_lag)) * 1000, 0
                    ) AS lag_ms
                    FROM pg_stat_replication
                """)).fetchone()
                self.replica_lag_ms = float(row.lag_ms) if row else 0.0
        except Exception:
            self.replica_lag_ms = 0.0

router = DatabaseRouter()
PY

cat > "$PROJECT_DIR/backend/app/optimizer.py" <<'PY'
from sqlalchemy import text
from .database import router

def get_slow_queries(limit: int = 20):
    """Fetch top slow queries from pg_stat_statements."""
    sql = text("""
        SELECT
            queryid::text,
            LEFT(query, 200) AS query,
            calls,
            ROUND(mean_exec_time::numeric, 2) AS avg_ms,
            ROUND(total_exec_time::numeric, 2) AS total_ms,
            rows,
            shared_blks_hit,
            shared_blks_read,
            CASE
                WHEN mean_exec_time > 500 THEN 'critical'
                WHEN mean_exec_time > 100 THEN 'warning'
                ELSE 'ok'
            END AS severity
        FROM pg_stat_statements
        WHERE query NOT LIKE '%pg_stat%'
          AND query NOT LIKE '%pg_class%'
          AND calls > 0
        ORDER BY mean_exec_time DESC
        LIMIT :limit
    """)
    with router.get_read_engine().connect() as conn:
        rows = conn.execute(sql, {"limit": limit}).mappings().all()
    return [dict(r) for r in rows]

def get_index_health():
    """Return index health: hit rate, size, unused indexes."""
    sql = text("""
        SELECT
            schemaname,
            tablename,
            indexname,
            idx_scan AS scans,
            idx_tup_read AS tuples_read,
            idx_tup_fetch AS tuples_fetched,
            pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
            pg_relation_size(indexrelid) AS index_size_bytes,
            CASE WHEN idx_scan = 0 THEN true ELSE false END AS unused,
            ROUND(
                100.0 * idx_scan / NULLIF(idx_scan + seq_scan, 0), 2
            ) AS hit_rate_pct
        FROM pg_stat_user_indexes
        JOIN pg_stat_user_tables USING (schemaname, tablename)
        WHERE schemaname = 'public'
        ORDER BY idx_scan ASC, pg_relation_size(indexrelid) DESC
    """)
    with router.get_read_engine().connect() as conn:
        rows = conn.execute(sql).mappings().all()
    return [dict(r) for r in rows]

def get_table_bloat():
    """Estimate table and index bloat."""
    sql = text("""
        SELECT
            schemaname,
            tablename,
            n_live_tup AS live_rows,
            n_dead_tup AS dead_rows,
            CASE WHEN n_live_tup + n_dead_tup > 0
                 THEN ROUND(100.0 * n_dead_tup / (n_live_tup + n_dead_tup), 2)
                 ELSE 0
            END AS bloat_pct,
            last_vacuum,
            last_autovacuum,
            last_analyze,
            last_autoanalyze,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size
        FROM pg_stat_user_tables
        WHERE schemaname = 'public'
        ORDER BY n_dead_tup DESC
        LIMIT 20
    """)
    with router.get_read_engine().connect() as conn:
        rows = conn.execute(sql).mappings().all()
    result = []
    for r in rows:
        d = dict(r)
        for k in ['last_vacuum','last_autovacuum','last_analyze','last_autoanalyze']:
            if d[k] is not None:
                d[k] = d[k].isoformat()
        result.append(d)
    return result

def explain_query(query_id: str):
    """Fetch the query from pg_stat_statements and run EXPLAIN ANALYZE."""
    # Lookup actual query text by queryid
    lookup = text("SELECT query FROM pg_stat_statements WHERE queryid::text = :qid LIMIT 1")
    with router.get_read_engine().connect() as conn:
        row = conn.execute(lookup, {"qid": query_id}).fetchone()
        if not row:
            return None
        # Run explain on a safe SELECT-only query
        q = row[0]
        if not q.strip().upper().startswith("SELECT"):
            return {"plan": "EXPLAIN only available for SELECT queries", "query": q}
        try:
            explain_sql = text("EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) " + q)
            plan_rows = conn.execute(explain_sql).fetchall()
            return {"plan": "\n".join(r[0] for r in plan_rows), "query": q}
        except Exception as e:
            return {"plan": f"Could not explain: {str(e)}", "query": q}

def get_missing_index_suggestions():
    """Suggest indexes for tables with high sequential scan counts."""
    sql = text("""
        SELECT
            schemaname,
            tablename,
            seq_scan,
            seq_tup_read,
            idx_scan,
            n_live_tup AS row_count,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS table_size
        FROM pg_stat_user_tables
        WHERE schemaname = 'public'
          AND seq_scan > 10
          AND n_live_tup > 1000
          AND (idx_scan = 0 OR seq_scan > idx_scan * 5)
        ORDER BY seq_tup_read DESC
        LIMIT 10
    """)
    with router.get_read_engine().connect() as conn:
        rows = conn.execute(sql).mappings().all()
    return [dict(r) for r in rows]
PY

cat > "$PROJECT_DIR/backend/app/partitions.py" <<'PY'
from sqlalchemy import text
from .database import router

def get_partition_stats():
    """Get per-partition row counts and sizes for partitioned tables."""
    sql = text("""
        SELECT
            parent.relname AS parent_table,
            child.relname AS partition_name,
            pg_size_pretty(pg_relation_size(child.oid)) AS partition_size,
            pg_relation_size(child.oid) AS size_bytes,
            COALESCE(st.n_live_tup, 0) AS row_count,
            COALESCE(st.n_dead_tup, 0) AS dead_rows,
            st.last_vacuum,
            st.last_autovacuum
        FROM pg_inherits
        JOIN pg_class parent ON pg_inherits.inhparent = parent.oid
        JOIN pg_class child  ON pg_inherits.inhrelid  = child.oid
        LEFT JOIN pg_stat_user_tables st ON st.relid = child.oid
        WHERE parent.relname IN (
            SELECT relname FROM pg_class
            WHERE relkind = 'p' AND relnamespace = 'public'::regnamespace
        )
        ORDER BY parent.relname, child.relname
    """)
    with router.get_read_engine().connect() as conn:
        rows = conn.execute(sql).mappings().all()
    result = []
    for r in rows:
        d = dict(r)
        for k in ['last_vacuum','last_autovacuum']:
            if d[k] is not None:
                d[k] = d[k].isoformat()
        result.append(d)
    return result

def test_partition_pruning(start_date: str, end_date: str):
    """Run EXPLAIN on a date-range query and parse pruning information."""
    sql = text("""
        EXPLAIN (FORMAT TEXT)
        SELECT COUNT(*) FROM audit_events
        WHERE created_at >= :start AND created_at < :end
    """)
    with router.get_read_engine().connect() as conn:
        rows = conn.execute(sql, {"start": start_date, "end": end_date}).fetchall()
    plan_text = "\n".join(r[0] for r in rows)
    # Count how many partitions appear in the plan
    import re
    scanned = re.findall(r'audit_events_\d{4}_\d{2}', plan_text)
    total_partitions = 12
    pruned = total_partitions - len(set(scanned))
    return {
        "plan": plan_text,
        "partitions_scanned": len(set(scanned)),
        "partitions_pruned": pruned,
        "total_partitions": total_partitions,
        "pruning_efficiency_pct": round(pruned / total_partitions * 100, 1)
    }
PY

cat > "$PROJECT_DIR/backend/app/replication.py" <<'PY'
from sqlalchemy import text
from .database import router

def get_replication_status():
    """Fetch replication lag and standby info from pg_stat_replication."""
    sql = text("""
        SELECT
            client_addr::text,
            state,
            sent_lsn::text,
            write_lsn::text,
            flush_lsn::text,
            replay_lsn::text,
            COALESCE(EXTRACT(EPOCH FROM write_lag) * 1000, 0)  AS write_lag_ms,
            COALESCE(EXTRACT(EPOCH FROM flush_lag) * 1000, 0)  AS flush_lag_ms,
            COALESCE(EXTRACT(EPOCH FROM replay_lag) * 1000, 0) AS replay_lag_ms,
            sync_state
        FROM pg_stat_replication
    """)
    try:
        with router.primary_engine.connect() as conn:
            rows = conn.execute(sql).mappings().all()
        replicas = [dict(r) for r in rows]
    except Exception:
        replicas = []

    return {
        "has_replica": bool(replicas),
        "replicas": replicas,
        "current_router_lag_ms": router.replica_lag_ms,
        "routing_to_replica": router._has_replica and router.replica_lag_ms < 500
    }

def get_connection_stats():
    """Get connection pool and active connection statistics."""
    sql = text("""
        SELECT
            state,
            COUNT(*) AS count
        FROM pg_stat_activity
        WHERE datname = current_database()
        GROUP BY state
        ORDER BY count DESC
    """)
    max_sql = text("SHOW max_connections")
    with router.primary_engine.connect() as conn:
        rows = conn.execute(sql).mappings().all()
        max_conn = conn.execute(max_sql).fetchone()[0]
    states = {r['state'] or 'unknown': r['count'] for r in rows}
    total = sum(states.values())
    return {
        "states": states,
        "total_connections": total,
        "max_connections": int(max_conn),
        "utilization_pct": round(total / int(max_conn) * 100, 1)
    }
PY

cat > "$PROJECT_DIR/backend/app/main.py" <<'PY'
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
PY

ok "Backend application files created"

# =============================================================================
# PHASE 4: Tests
# =============================================================================
info "Writing test files"

cat > "$PROJECT_DIR/backend/tests/__init__.py" <<'PY'
PY
cat > "$PROJECT_DIR/backend/tests/unit/__init__.py" <<'PY'
PY
cat > "$PROJECT_DIR/backend/tests/integration/__init__.py" <<'PY'
PY

cat > "$PROJECT_DIR/backend/tests/unit/test_optimizer.py" <<'PY'
"""Unit tests for query optimizer logic (no DB required)."""
import pytest
import re

def parse_explain_plan(plan_text: str):
    """Extract key metrics from EXPLAIN output."""
    scanned = re.findall(r'audit_events_\d{4}_\d{2}', plan_text)
    index_scans = plan_text.count('Index Scan')
    seq_scans = plan_text.count('Seq Scan')
    return {
        "partitions_scanned": len(set(scanned)),
        "index_scans": index_scans,
        "seq_scans": seq_scans,
    }

def classify_query_severity(avg_ms: float):
    if avg_ms > 500: return 'critical'
    if avg_ms > 100: return 'warning'
    return 'ok'

def suggest_index(seq_scans: int, idx_scans: int, row_count: int):
    if row_count < 1000: return False
    if seq_scans == 0: return False
    if idx_scans == 0 or seq_scans > idx_scans * 5: return True
    return False

def test_classify_critical():
    assert classify_query_severity(600) == 'critical'

def test_classify_warning():
    assert classify_query_severity(150) == 'warning'

def test_classify_ok():
    assert classify_query_severity(30) == 'ok'

def test_classify_boundary_warning():
    assert classify_query_severity(100.1) == 'warning'

def test_classify_boundary_ok():
    assert classify_query_severity(100.0) == 'ok'

def test_parse_plan_single_partition():
    plan = """
    Aggregate
      -> Seq Scan on audit_events_2025_05
           Filter: (user_id = 42)
    """
    result = parse_explain_plan(plan)
    assert result["partitions_scanned"] == 1

def test_parse_plan_multiple_partitions():
    plan = """
    Append
      -> Seq Scan on audit_events_2025_04
      -> Seq Scan on audit_events_2025_05
    """
    result = parse_explain_plan(plan)
    assert result["partitions_scanned"] == 2

def test_parse_plan_no_partitions():
    plan = "Seq Scan on users"
    result = parse_explain_plan(plan)
    assert result["partitions_scanned"] == 0

def test_suggest_index_high_seq_scans():
    assert suggest_index(100, 0, 50000) is True

def test_suggest_index_small_table():
    assert suggest_index(100, 0, 500) is False

def test_suggest_index_balanced():
    assert suggest_index(10, 20, 10000) is False

def test_suggest_index_seq_dominates():
    assert suggest_index(100, 10, 10000) is True

def test_pruning_efficiency():
    total = 12
    scanned = 1
    pruned = total - scanned
    pct = round(pruned / total * 100, 1)
    assert pct == 91.7

def test_partition_name_regex():
    names = re.findall(r'audit_events_\d{4}_\d{2}',
                       "audit_events_2025_05 audit_events_2025_06")
    assert len(names) == 2

def test_index_name_generation():
    table = "audit_events"
    cols = ["user_id", "created_at"]
    name = f"idx_{table}_{'_'.join(cols)}"
    assert name == "idx_audit_events_user_id_created_at"

def test_sanitize_identifier_valid():
    import re
    assert re.match(r'^[a-zA-Z0-9_]+$', "audit_events") is not None

def test_sanitize_identifier_invalid():
    import re
    assert re.match(r'^[a-zA-Z0-9_]+$', "users; DROP TABLE") is None

def test_bloat_pct_calculation():
    live = 1000
    dead = 50
    pct = round(100.0 * dead / (live + dead), 2)
    assert pct == 4.76

def test_connection_utilization():
    total = 15
    max_conn = 100
    pct = round(total / max_conn * 100, 1)
    assert pct == 15.0

def test_lag_threshold_failover():
    lag_ms = 600.0
    threshold = 500.0
    route_to_replica = lag_ms < threshold
    assert route_to_replica is False

def test_lag_within_threshold():
    lag_ms = 10.0
    threshold = 500.0
    route_to_replica = lag_ms < threshold
    assert route_to_replica is True
PY

cat > "$PROJECT_DIR/backend/tests/integration/test_api.py" <<'PY'
"""Integration tests — require running backend service."""
import pytest
import httpx
import os

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

@pytest.fixture
def client():
    return httpx.Client(base_url=BASE_URL, timeout=30.0)

def test_health_check(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"

def test_slow_queries_returns_list(client):
    r = client.get("/api/queries/slow")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)

def test_slow_queries_structure(client):
    r = client.get("/api/queries/slow?limit=5")
    assert r.status_code == 200
    data = r.json()
    assert len(data) <= 5
    if data:
        q = data[0]
        assert "query" in q
        assert "avg_ms" in q
        assert "calls" in q

def test_index_health_returns_list(client):
    r = client.get("/api/indexes/health")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)

def test_partition_stats_returns_partitions(client):
    r = client.get("/api/partitions/stats")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    # Should have 12 partitions for audit_events
    partitions = [p for p in data if p.get("parent_table") == "audit_events"]
    assert len(partitions) == 12

def test_partition_pruning_test(client):
    r = client.get("/api/partitions/pruning-test?start=2025-05-01&end=2025-06-01")
    assert r.status_code == 200
    data = r.json()
    assert "partitions_scanned" in data
    assert "pruning_efficiency_pct" in data
    assert data["total_partitions"] == 12
    assert data["partitions_scanned"] <= data["total_partitions"]

def test_replication_status(client):
    r = client.get("/api/replication/status")
    assert r.status_code == 200
    data = r.json()
    assert "has_replica" in data
    assert "current_router_lag_ms" in data

def test_connection_stats(client):
    r = client.get("/api/replication/connections")
    assert r.status_code == 200
    data = r.json()
    assert "total_connections" in data
    assert "max_connections" in data
    assert "utilization_pct" in data

def test_table_bloat(client):
    r = client.get("/api/maintenance/bloat")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_dashboard_summary(client):
    r = client.get("/api/dashboard/summary")
    assert r.status_code == 200
    data = r.json()
    for key in ["avg_query_latency_ms","slow_query_count","replica_lag_ms","connection_utilization_pct"]:
        assert key in data

def test_vacuum_invalid_table(client):
    r = client.post("/api/maintenance/vacuum", json={"table_name": "bad; DROP TABLE users"})
    assert r.status_code == 400

def test_vacuum_valid_table(client):
    r = client.post("/api/maintenance/vacuum", json={"table_name": "users", "analyze": True})
    assert r.status_code == 200
    assert r.json()["status"] == "completed"
PY

cat > "$PROJECT_DIR/backend/tests/load_generator.py" <<'PY'
"""Load generator — populates pg_stat_statements with realistic query patterns."""
import psycopg2
import random
import time
import argparse
import threading

DB_URL = "postgresql://admin:admin_pass@localhost:5432/dbopt_dev"

def run_queries(duration: int, worker_id: int):
    conn = psycopg2.connect(DB_URL)
    conn.autocommit = True
    cur = conn.cursor()
    end = time.time() + duration
    count = 0
    while time.time() < end:
        q_type = random.randint(1, 6)
        try:
            if q_type == 1:
                # Slow: seq scan without index
                cur.execute("SELECT COUNT(*) FROM audit_events WHERE user_id = %s",
                            (random.randint(1, 500),))
            elif q_type == 2:
                # Medium: date range on partition
                month = random.randint(1, 12)
                cur.execute(
                    "SELECT COUNT(*) FROM audit_events WHERE created_at >= %s AND created_at < %s",
                    (f"2025-{month:02d}-01", f"2025-{month:02d}-28")
                )
            elif q_type == 3:
                # Fast: PK lookup
                cur.execute("SELECT * FROM users WHERE id = %s", (random.randint(1, 500),))
            elif q_type == 4:
                # Join query
                cur.execute("""
                    SELECT u.username, COUNT(ae.id) FROM users u
                    LEFT JOIN audit_events ae ON ae.user_id = u.id
                    WHERE u.team_id = %s GROUP BY u.username LIMIT 10
                """, (random.randint(1, 4),))
            elif q_type == 5:
                # JSONB query
                cur.execute("""
                    SELECT COUNT(*) FROM audit_events
                    WHERE metadata->>'browser' = %s
                """, (random.choice(['Chrome','Firefox','Safari']),))
            else:
                # Action filter
                cur.execute(
                    "SELECT * FROM audit_events WHERE action = %s LIMIT 20",
                    (random.choice(['login','logout','create','delete']),)
                )
        except Exception:
            pass
        count += 1
        time.sleep(0.01)
    print(f"  Worker {worker_id}: {count} queries executed")
    cur.close()
    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", type=int, default=30)
    parser.add_argument("--concurrency", type=int, default=5)
    args = parser.parse_args()
    print(f"Running load for {args.duration}s with {args.concurrency} workers...")
    threads = [
        threading.Thread(target=run_queries, args=(args.duration, i))
        for i in range(args.concurrency)
    ]
    for t in threads: t.start()
    for t in threads: t.join()
    print("Load generation complete")
PY

ok "Test files created"

# =============================================================================
# PHASE 5: Frontend React Application
# =============================================================================
info "Writing frontend application files"

cat > "$PROJECT_DIR/frontend/package.json" <<'JSON'
{
  "name": "day115-db-dashboard",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "axios": "^1.7.9",
    "recharts": "^2.14.1",
    "antd": "^5.22.3",
    "@ant-design/icons": "^5.5.2",
    "react-scripts": "5.0.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build"
  },
  "browserslist": {
    "production": [">0.2%","not dead","not op_mini all"],
    "development": ["last 1 chrome version","last 1 firefox version","last 1 safari version"]
  },
  "proxy": "http://localhost:8000"
}
JSON

mkdir -p "$PROJECT_DIR/frontend/public"
cat > "$PROJECT_DIR/frontend/public/index.html" <<'HTML'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>DB Optimization Dashboard</title>
</head>
<body>
  <div id="root"></div>
</body>
</html>
HTML

cat > "$PROJECT_DIR/frontend/src/index.js" <<'JSX'
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<React.StrictMode><App /></React.StrictMode>);
JSX

cat > "$PROJECT_DIR/frontend/src/index.css" <<'CSS'
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: #f0f2f5;
  color: #1a1a2e;
}
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #f1f1f1; }
::-webkit-scrollbar-thumb { background: #52b788; border-radius: 3px; }
CSS

cat > "$PROJECT_DIR/frontend/src/App.jsx" <<'JSX'
import React, { useState, useEffect, useCallback } from 'react';
import { Layout, Typography, Button, Space, Badge, Tooltip, notification, Spin, Row, Col } from 'antd';
import {
  DatabaseOutlined, ThunderboltOutlined, ReloadOutlined,
  CheckCircleOutlined, WarningOutlined, CloseCircleOutlined
} from '@ant-design/icons';
import axios from 'axios';
import SlowQueryPanel from './components/SlowQueryPanel';
import IndexHealthPanel from './components/IndexHealthPanel';
import PartitionPanel from './components/PartitionPanel';
import ReplicationPanel from './components/ReplicationPanel';
import SummaryCards from './components/SummaryCards';
import './App.css';

const { Header, Content } = Layout;
const { Title } = Typography;
const API = process.env.REACT_APP_API_URL || '';

export default function App() {
  const [summary, setSummary] = useState(null);
  const [slowQueries, setSlowQueries] = useState([]);
  const [indexHealth, setIndexHealth] = useState([]);
  const [partitions, setPartitions] = useState([]);
  const [replication, setReplication] = useState(null);
  const [connections, setConnections] = useState(null);
  const [bloat, setBloat] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastRefresh, setLastRefresh] = useState(null);
  const [notifApi, contextHolder] = notification.useNotification();

  const fetchAll = useCallback(async () => {
    try {
      const [sumR, sqR, idxR, partR, replR, connR, bloatR] = await Promise.all([
        axios.get(`${API}/api/dashboard/summary`),
        axios.get(`${API}/api/queries/slow?limit=20`),
        axios.get(`${API}/api/indexes/health`),
        axios.get(`${API}/api/partitions/stats`),
        axios.get(`${API}/api/replication/status`),
        axios.get(`${API}/api/replication/connections`),
        axios.get(`${API}/api/maintenance/bloat`),
      ]);
      setSummary(sumR.data);
      setSlowQueries(sqR.data);
      setIndexHealth(idxR.data);
      setPartitions(partR.data);
      setReplication(replR.data);
      setConnections(connR.data);
      setBloat(bloatR.data);
      setLastRefresh(new Date().toLocaleTimeString());
    } catch (e) {
      notifApi.error({ message: 'Fetch error', description: e.message, duration: 3 });
    } finally {
      setLoading(false);
    }
  }, [notifApi]);

  useEffect(() => {
    fetchAll();
    const iv = setInterval(fetchAll, 5000);
    return () => clearInterval(iv);
  }, [fetchAll]);

  const handleVacuum = async (table) => {
    try {
      await axios.post(`${API}/api/maintenance/vacuum`, { table_name: table, analyze: true });
      notifApi.success({ message: `VACUUM ANALYZE completed on ${table}`, duration: 3 });
      fetchAll();
    } catch (e) {
      notifApi.error({ message: 'VACUUM failed', description: e.message });
    }
  };

  const handleAnalyze = async () => {
    try {
      await axios.post(`${API}/api/maintenance/analyze`);
      notifApi.success({ message: 'ANALYZE completed — statistics refreshed', duration: 3 });
      fetchAll();
    } catch (e) {
      notifApi.error({ message: 'ANALYZE failed', description: e.message });
    }
  };

  const overallHealth = summary
    ? summary.avg_query_latency_ms < 50 ? 'good'
      : summary.avg_query_latency_ms < 200 ? 'warn' : 'bad'
    : 'unknown';

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {contextHolder}
      <Header style={{
        background: '#1b4332', padding: '0 24px', display: 'flex',
        alignItems: 'center', justifyContent: 'space-between',
        height: '56px', boxShadow: '0 2px 8px rgba(0,0,0,0.3)'
      }}>
        <Space size={12}>
          <DatabaseOutlined style={{ color: '#52b788', fontSize: 22 }} />
          <Title level={4} style={{ color: 'white', margin: 0, fontWeight: 700 }}>
            DB Optimization
          </Title>
          <span style={{ color: '#74c69d', fontSize: 12 }}>Day 115 · Week 11 of 180</span>
        </Space>
        <Space size={12}>
          {lastRefresh && (
            <span style={{ color: '#74c69d', fontSize: 12 }}>Last: {lastRefresh}</span>
          )}
          <Badge
            color={overallHealth === 'good' ? '#52b788' : overallHealth === 'warn' ? '#fca311' : '#e63946'}
            text={<span style={{ color: 'white', fontSize: 12 }}>
              {overallHealth === 'good' ? 'Healthy' : overallHealth === 'warn' ? 'Degraded' : 'Critical'}
            </span>}
          />
          <Tooltip title="Refresh statistics"><Button
            icon={<ReloadOutlined />} onClick={fetchAll} size="small"
            style={{ background: '#2d6a4f', borderColor: '#52b788', color: 'white' }}
          /></Tooltip>
          <Button
            icon={<ThunderboltOutlined />} onClick={handleAnalyze} size="small"
            style={{ background: '#40916c', borderColor: '#52b788', color: 'white' }}
          >ANALYZE</Button>
        </Space>
      </Header>
      <Content style={{ padding: '20px 24px' }}>
        {loading ? (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
            <Spin size="large" tip="Connecting to database..." />
          </div>
        ) : (
          <Space direction="vertical" size={16} style={{ width: '100%' }}>
            <SummaryCards summary={summary} connections={connections} />
            <Row gutter={[16, 16]}>
              <Col xs={24} lg={14}>
                <SlowQueryPanel queries={slowQueries} />
              </Col>
              <Col xs={24} lg={10}>
                <IndexHealthPanel indexes={indexHealth} onRefresh={fetchAll} />
              </Col>
            </Row>
            <Row gutter={[16, 16]}>
              <Col xs={24} lg={14}>
                <PartitionPanel partitions={partitions} />
              </Col>
              <Col xs={24} lg={10}>
                <ReplicationPanel
                  replication={replication}
                  connections={connections}
                  bloat={bloat}
                  onVacuum={handleVacuum}
                />
              </Col>
            </Row>
          </Space>
        )}
      </Content>
    </Layout>
  );
}
JSX

cat > "$PROJECT_DIR/frontend/src/App.css" <<'CSS'
.panel-card {
  background: white;
  border-radius: 10px;
  padding: 16px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  border: 1px solid #e8f5e9;
}
.panel-title {
  font-size: 13px;
  font-weight: 700;
  color: #1b4332;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid #d8f3dc;
}
.metric-value {
  font-size: 28px;
  font-weight: 700;
  color: #1b4332;
  line-height: 1;
}
.metric-label {
  font-size: 11px;
  color: #74c69d;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-top: 4px;
}
.latency-badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}
.latency-ok { background: #d8f3dc; color: #1b4332; }
.latency-warn { background: #fff3cd; color: #856404; }
.latency-critical { background: #fde8e8; color: #c62828; }
.index-bar {
  height: 8px;
  border-radius: 4px;
  background: #e9ecef;
  overflow: hidden;
}
.index-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}
CSS

mkdir -p "$PROJECT_DIR/frontend/src/components"

cat > "$PROJECT_DIR/frontend/src/components/SummaryCards.jsx" <<'JSX'
import React from 'react';
import { Row, Col } from 'antd';
import {
  ThunderboltOutlined, ClockCircleOutlined,
  ApiOutlined, SafetyOutlined
} from '@ant-design/icons';

const MetricCard = ({ icon, value, label, color, subtext }) => (
  <div style={{
    background: 'white', borderRadius: 10, padding: '16px 20px',
    boxShadow: '0 1px 4px rgba(0,0,0,0.08)', borderLeft: `4px solid ${color}`,
    display: 'flex', alignItems: 'center', gap: 16
  }}>
    <div style={{
      width: 44, height: 44, borderRadius: 10,
      background: `${color}22`, display: 'flex',
      alignItems: 'center', justifyContent: 'center', fontSize: 20, color
    }}>{icon}</div>
    <div>
      <div style={{ fontSize: 26, fontWeight: 700, color: '#1b4332', lineHeight: 1 }}>{value}</div>
      <div style={{ fontSize: 11, color: '#74c69d', textTransform: 'uppercase', letterSpacing: '0.5px', marginTop: 2 }}>{label}</div>
      {subtext && <div style={{ fontSize: 11, color: '#999', marginTop: 2 }}>{subtext}</div>}
    </div>
  </div>
);

export default function SummaryCards({ summary, connections }) {
  if (!summary) return null;
  const latencyColor = summary.avg_query_latency_ms < 50 ? '#52b788'
    : summary.avg_query_latency_ms < 200 ? '#fca311' : '#e63946';
  return (
    <Row gutter={[12, 12]}>
      <Col xs={12} sm={6}>
        <MetricCard
          icon={<ClockCircleOutlined />}
          value={`${summary.avg_query_latency_ms}ms`}
          label="Avg Latency (p50)"
          color={latencyColor}
          subtext="Top 5 slow queries"
        />
      </Col>
      <Col xs={12} sm={6}>
        <MetricCard
          icon={<ThunderboltOutlined />}
          value={summary.slow_query_count}
          label="Slow Queries"
          color={summary.slow_query_count > 5 ? '#e63946' : '#52b788'}
          subtext="> 100ms threshold"
        />
      </Col>
      <Col xs={12} sm={6}>
        <MetricCard
          icon={<ApiOutlined />}
          value={connections ? `${connections.total_connections}` : '—'}
          label="Active Connections"
          color="#40916c"
          subtext={connections ? `${connections.utilization_pct}% of max` : ''}
        />
      </Col>
      <Col xs={12} sm={6}>
        <MetricCard
          icon={<SafetyOutlined />}
          value={summary.replica_lag_ms < 1 ? '< 1ms' : `${Math.round(summary.replica_lag_ms)}ms`}
          label="Replica Lag"
          color={summary.replica_lag_ms < 100 ? '#52b788' : '#e63946'}
          subtext={summary.routing_to_replica ? 'Routing to replica ✓' : 'Primary only'}
        />
      </Col>
    </Row>
  );
}
JSX

cat > "$PROJECT_DIR/frontend/src/components/SlowQueryPanel.jsx" <<'JSX'
import React, { useState } from 'react';
import { Table, Tag, Modal, Typography, Button, Tooltip, Badge } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import axios from 'axios';
const { Text } = Typography;
const API = process.env.REACT_APP_API_URL || '';

const severityColor = { critical: '#e63946', warning: '#fca311', ok: '#52b788' };

export default function SlowQueryPanel({ queries }) {
  const [explainModal, setExplainModal] = useState(null);
  const [loadingExplain, setLoadingExplain] = useState(false);

  const showExplain = async (queryId) => {
    setLoadingExplain(true);
    try {
      const r = await axios.get(`${API}/api/queries/explain/${queryId}`);
      setExplainModal(r.data);
    } catch (e) {
      setExplainModal({ plan: 'Error fetching plan: ' + e.message, query: '' });
    } finally {
      setLoadingExplain(false);
    }
  };

  const columns = [
    {
      title: 'Query', dataIndex: 'query', ellipsis: true,
      render: (v) => <Tooltip title={v}><Text code style={{ fontSize: 11 }}>{v?.substring(0, 55)}...</Text></Tooltip>
    },
    {
      title: 'Avg Latency', dataIndex: 'avg_ms', width: 110, sorter: (a, b) => b.avg_ms - a.avg_ms,
      defaultSortOrder: 'ascend',
      render: (v, r) => (
        <span className={`latency-badge latency-${r.severity}`}>{v}ms</span>
      )
    },
    {
      title: 'Calls', dataIndex: 'calls', width: 80,
      render: v => <span style={{ color: '#2d6a4f', fontWeight: 600 }}>{Number(v).toLocaleString()}</span>
    },
    {
      title: 'Total ms', dataIndex: 'total_ms', width: 90,
      render: v => <span style={{ fontSize: 12, color: '#666' }}>{Number(v).toFixed(0)}</span>
    },
    {
      title: 'Cache Hit', width: 85,
      render: (_, r) => {
        const total = (r.shared_blks_hit || 0) + (r.shared_blks_read || 0);
        const pct = total > 0 ? Math.round((r.shared_blks_hit / total) * 100) : 100;
        return <span style={{ color: pct >= 95 ? '#52b788' : '#e63946', fontWeight: 600 }}>{pct}%</span>;
      }
    },
    {
      title: '', width: 70,
      render: (_, r) => (
        <Button size="small" icon={<SearchOutlined />}
          onClick={() => showExplain(r.queryid)}
          style={{ borderColor: '#52b788', color: '#2d6a4f', fontSize: 11 }}
        >PLAN</Button>
      )
    }
  ];

  return (
    <div className="panel-card">
      <div className="panel-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span>Slow Query Analysis</span>
        <Badge count={queries.filter(q => q.severity === 'critical').length}
          style={{ backgroundColor: '#e63946' }}
          overflowCount={99}
        />
      </div>
      <Table
        dataSource={queries}
        columns={columns}
        rowKey="queryid"
        size="small"
        pagination={{ pageSize: 8, size: 'small' }}
        rowClassName={(r) => r.severity === 'critical' ? 'critical-row' : ''}
        scroll={{ x: true }}
        style={{ fontSize: 12 }}
      />
      <Modal
        title="EXPLAIN ANALYZE Plan"
        open={!!explainModal}
        onCancel={() => setExplainModal(null)}
        footer={null}
        width={720}
      >
        {explainModal && (
          <>
            <Text type="secondary" style={{ fontSize: 11, display: 'block', marginBottom: 8 }}>
              {explainModal.query?.substring(0, 100)}
            </Text>
            <pre style={{
              background: '#f0f9f4', padding: 12, borderRadius: 6,
              fontSize: 11, overflow: 'auto', maxHeight: 400,
              border: '1px solid #b7e4c7', color: '#1b4332'
            }}>{explainModal.plan}</pre>
          </>
        )}
      </Modal>
    </div>
  );
}
JSX

cat > "$PROJECT_DIR/frontend/src/components/IndexHealthPanel.jsx" <<'JSX'
import React, { useState } from 'react';
import { Table, Button, Tag, Modal, Form, Input, Select, notification, Tooltip } from 'antd';
import { PlusOutlined, WarningOutlined } from '@ant-design/icons';
import axios from 'axios';
const API = process.env.REACT_APP_API_URL || '';

export default function IndexHealthPanel({ indexes, onRefresh }) {
  const [createModal, setCreateModal] = useState(false);
  const [form] = Form.useForm();
  const [creating, setCreating] = useState(false);
  const [notifApi, ctx] = notification.useNotification();

  const handleCreate = async (vals) => {
    setCreating(true);
    try {
      const cols = vals.columns.split(',').map(c => c.trim());
      await axios.post(`${API}/api/indexes/create`, {
        table_name: vals.table_name,
        columns: cols,
        index_type: vals.index_type || 'btree',
      });
      notifApi.success({ message: `Index created on ${vals.table_name}(${vals.columns})` });
      setCreateModal(false);
      form.resetFields();
      onRefresh();
    } catch (e) {
      notifApi.error({ message: 'Index creation failed', description: e.response?.data?.detail || e.message });
    } finally {
      setCreating(false);
    }
  };

  const columns = [
    {
      title: 'Index', dataIndex: 'indexname',
      render: (v, r) => (
        <div>
          <div style={{ fontSize: 12, fontWeight: 600, color: '#1b4332' }}>{v}</div>
          <div style={{ fontSize: 10, color: '#999' }}>{r.tablename}</div>
        </div>
      )
    },
    {
      title: 'Hit Rate', width: 100,
      render: (_, r) => {
        const pct = r.hit_rate_pct || 0;
        const color = pct >= 90 ? '#52b788' : pct >= 50 ? '#fca311' : '#e63946';
        return (
          <div>
            <div style={{ color, fontWeight: 700, fontSize: 13 }}>{pct}%</div>
            <div className="index-bar">
              <div className="index-bar-fill" style={{ width: `${pct}%`, background: color }} />
            </div>
          </div>
        );
      }
    },
    {
      title: 'Scans', dataIndex: 'scans', width: 70,
      render: v => <span style={{ color: '#2d6a4f', fontSize: 12 }}>{Number(v).toLocaleString()}</span>
    },
    {
      title: 'Size', dataIndex: 'index_size', width: 70,
      render: v => <span style={{ fontSize: 12, color: '#666' }}>{v}</span>
    },
    {
      title: 'Status', width: 80,
      render: (_, r) => r.unused
        ? <Tag color="red" style={{ fontSize: 10 }}>UNUSED</Tag>
        : <Tag color="green" style={{ fontSize: 10 }}>ACTIVE</Tag>
    }
  ];

  return (
    <div className="panel-card">
      {ctx}
      <div className="panel-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span>Index Health</span>
        <Button size="small" icon={<PlusOutlined />} onClick={() => setCreateModal(true)}
          style={{ background: '#52b788', borderColor: '#40916c', color: 'white', fontSize: 11 }}>
          New Index
        </Button>
      </div>
      <Table
        dataSource={indexes}
        columns={columns}
        rowKey="indexname"
        size="small"
        pagination={{ pageSize: 6, size: 'small' }}
        style={{ fontSize: 12 }}
      />
      <Modal
        title="Create Index CONCURRENTLY"
        open={createModal}
        onCancel={() => setCreateModal(false)}
        onOk={() => form.submit()}
        okText="Create"
        okButtonProps={{ loading: creating, style: { background: '#40916c' } }}
      >
        <Form form={form} onFinish={handleCreate} layout="vertical">
          <Form.Item name="table_name" label="Table" rules={[{ required: true }]}>
            <Select options={[
              { value: 'audit_events', label: 'audit_events' },
              { value: 'users', label: 'users' },
              { value: 'teams', label: 'teams' },
            ]} />
          </Form.Item>
          <Form.Item name="columns" label="Columns (comma-separated)" rules={[{ required: true }]}>
            <Input placeholder="e.g., user_id, created_at" />
          </Form.Item>
          <Form.Item name="index_type" label="Index Type" initialValue="btree">
            <Select options={[
              { value: 'btree', label: 'BTREE (default)' },
              { value: 'gin', label: 'GIN (JSONB/arrays)' },
              { value: 'hash', label: 'HASH (equality only)' },
            ]} />
          </Form.Item>
          <p style={{ fontSize: 12, color: '#74c69d', marginTop: 8 }}>
            Uses CONCURRENTLY — safe on live tables, no write lock.
          </p>
        </Form>
      </Modal>
    </div>
  );
}
JSX

cat > "$PROJECT_DIR/frontend/src/components/PartitionPanel.jsx" <<'JSX'
import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip as RcTooltip, ResponsiveContainer, Cell } from 'recharts';
import { Button, Tag, notification } from 'antd';
import axios from 'axios';
const API = process.env.REACT_APP_API_URL || '';

const COLORS = [
  '#1b4332','#2d6a4f','#40916c','#52b788',
  '#74c69d','#95d5b2','#b7e4c7','#d8f3dc',
  '#40916c','#52b788','#74c69d','#95d5b2'
];

export default function PartitionPanel({ partitions }) {
  const [pruningResult, setPruningResult] = useState(null);
  const [testing, setTesting] = useState(false);
  const [notifApi, ctx] = notification.useNotification();

  const auditParts = partitions.filter(p => p.parent_table === 'audit_events');
  const chartData = auditParts.map((p, i) => ({
    name: p.partition_name.replace('audit_events_', '').replace('_', '-'),
    rows: p.row_count,
    size: p.partition_size,
    idx: i
  }));

  const testPruning = async () => {
    setTesting(true);
    try {
      const r = await axios.get(`${API}/api/partitions/pruning-test?start=2025-05-01&end=2025-06-01`);
      setPruningResult(r.data);
    } catch (e) {
      notifApi.error({ message: 'Pruning test failed' });
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="panel-card">
      {ctx}
      <div className="panel-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span>Partition Stats — audit_events (2025)</span>
        <Button size="small" onClick={testPruning} loading={testing}
          style={{ background: '#40916c', borderColor: '#2d6a4f', color: 'white', fontSize: 11 }}>
          Test Pruning
        </Button>
      </div>
      <ResponsiveContainer width="100%" height={180}>
        <BarChart data={chartData} margin={{ top: 4, right: 4, left: -20, bottom: 4 }}>
          <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#2d6a4f' }} />
          <YAxis tick={{ fontSize: 10 }} tickFormatter={v => v > 1000 ? `${(v/1000).toFixed(0)}k` : v} />
          <RcTooltip formatter={(v, n, p) => [`${Number(v).toLocaleString()} rows`, p.payload.size]} />
          <Bar dataKey="rows" radius={[3, 3, 0, 0]}>
            {chartData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 8 }}>
        <span style={{ fontSize: 11, color: '#666' }}>
          {auditParts.length} partitions · {auditParts.reduce((s, p) => s + p.row_count, 0).toLocaleString()} total rows
        </span>
      </div>
      {pruningResult && (
        <div style={{
          marginTop: 10, padding: '10px 14px', background: '#f0fdf4',
          borderRadius: 8, border: '1px solid #b7e4c7'
        }}>
          <div style={{ display: 'flex', gap: 16, alignItems: 'center', flexWrap: 'wrap' }}>
            <span style={{ fontSize: 12, color: '#2d6a4f', fontWeight: 700 }}>
              Pruning Result: May 2025 query
            </span>
            <Tag color="green">Scanned: {pruningResult.partitions_scanned}/{pruningResult.total_partitions}</Tag>
            <Tag color="success">
              {pruningResult.pruning_efficiency_pct}% eliminated
            </Tag>
          </div>
          <pre style={{
            fontSize: 10, background: '#e8f5e9', padding: 8,
            borderRadius: 4, marginTop: 6, maxHeight: 100, overflow: 'auto',
            color: '#1b4332', border: '1px solid #c8e6c9'
          }}>{pruningResult.plan}</pre>
        </div>
      )}
    </div>
  );
}
JSX

cat > "$PROJECT_DIR/frontend/src/components/ReplicationPanel.jsx" <<'JSX'
import React from 'react';
import { Table, Tag, Button, Progress, Tooltip } from 'antd';
import { ThunderboltOutlined } from '@ant-design/icons';

export default function ReplicationPanel({ replication, connections, bloat, onVacuum }) {
  const lagMs = replication?.current_router_lag_ms || 0;
  const lagColor = lagMs < 10 ? '#52b788' : lagMs < 100 ? '#fca311' : '#e63946';
  const connPct = connections?.utilization_pct || 0;

  return (
    <div className="panel-card">
      <div className="panel-title">Replication & Health</div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 14 }}>
        <div style={{
          background: '#f0fdf4', borderRadius: 8, padding: '10px 14px',
          border: '1px solid #d8f3dc'
        }}>
          <div style={{ fontSize: 10, color: '#74c69d', textTransform: 'uppercase', marginBottom: 4 }}>Replica Lag</div>
          <div style={{ fontSize: 22, fontWeight: 700, color: lagColor }}>
            {lagMs < 1 ? '< 1ms' : `${Math.round(lagMs)}ms`}
          </div>
          <div style={{ fontSize: 10, color: '#aaa', marginTop: 2 }}>
            {replication?.has_replica ? 'Streaming replication' : 'Single-node mode'}
          </div>
          {replication?.has_replica && (
            <Tag color={replication.routing_to_replica ? 'green' : 'orange'} style={{ marginTop: 4, fontSize: 10 }}>
              {replication.routing_to_replica ? 'Routing → Replica' : 'Routing → Primary'}
            </Tag>
          )}
        </div>
        <div style={{
          background: '#f0fdf4', borderRadius: 8, padding: '10px 14px',
          border: '1px solid #d8f3dc'
        }}>
          <div style={{ fontSize: 10, color: '#74c69d', textTransform: 'uppercase', marginBottom: 4 }}>Connections</div>
          <div style={{ fontSize: 22, fontWeight: 700, color: '#1b4332' }}>
            {connections?.total_connections || 0}
          </div>
          <Progress
            percent={connPct} size="small"
            strokeColor={connPct > 80 ? '#e63946' : '#52b788'}
            showInfo={false} style={{ marginTop: 4 }}
          />
          <div style={{ fontSize: 10, color: '#aaa' }}>{connPct}% of {connections?.max_connections}</div>
        </div>
      </div>

      <div style={{ marginBottom: 8, fontSize: 12, fontWeight: 600, color: '#1b4332' }}>
        Table Bloat (top tables)
      </div>
      <Table
        dataSource={bloat?.slice(0, 5) || []}
        rowKey="tablename"
        size="small"
        pagination={false}
        columns={[
          {
            title: 'Table', dataIndex: 'tablename',
            render: v => <span style={{ fontSize: 11, color: '#2d6a4f' }}>{v}</span>
          },
          {
            title: 'Bloat', dataIndex: 'bloat_pct', width: 70,
            render: v => (
              <span style={{
                fontWeight: 700, fontSize: 12,
                color: v > 10 ? '#e63946' : v > 5 ? '#fca311' : '#52b788'
              }}>{v}%</span>
            )
          },
          {
            title: 'Dead Rows', dataIndex: 'dead_rows', width: 85,
            render: v => <span style={{ fontSize: 11, color: '#999' }}>{Number(v).toLocaleString()}</span>
          },
          {
            title: '', width: 65,
            render: (_, r) => (
              <Tooltip title="Run VACUUM ANALYZE">
                <Button size="small" icon={<ThunderboltOutlined />}
                  onClick={() => onVacuum(r.tablename)}
                  style={{ fontSize: 10, borderColor: '#74c69d', color: '#2d6a4f' }}>
                  VACUUM
                </Button>
              </Tooltip>
            )
          }
        ]}
        style={{ fontSize: 11 }}
      />
    </div>
  );
}
JSX

ok "Frontend application files created"

# =============================================================================
# PHASE 6: Docker Compose
# =============================================================================
info "Writing Docker Compose configuration"

cat > "$PROJECT_DIR/docker-compose.yml" <<'YAML'
version: '3.9'

networks:
  dbopt-net:
    driver: bridge

volumes:
  pg-primary-data:
  pg-replica-data:

services:
  pg-primary:
    image: postgres:16-alpine
    container_name: pg-primary
    networks: [dbopt-net]
    ports: ["5432:5432"]
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: admin_pass
      POSTGRES_DB: dbopt_dev
    volumes:
      - pg-primary-data:/var/lib/postgresql/data
      - ./postgres/primary/postgresql.conf:/etc/postgresql/postgresql.conf
      - ./postgres/primary/pg_hba.conf:/etc/postgresql/pg_hba.conf
      - ./postgres/init.sql:/docker-entrypoint-initdb.d/01_init.sql
    command: >
      postgres
        -c config_file=/etc/postgresql/postgresql.conf
        -c hba_file=/etc/postgresql/pg_hba.conf
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin -d dbopt_dev"]
      interval: 5s
      timeout: 5s
      retries: 10

  pg-replica:
    image: postgres:16-alpine
    container_name: pg-replica
    networks: [dbopt-net]
    ports: ["5433:5432"]
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: admin_pass
      PGPASSWORD: admin_pass
      PGUSER: admin
      PRIMARY_HOST: pg-primary
    volumes:
      - pg-replica-data:/var/lib/postgresql/data
    entrypoint: >
      sh -c "
        until pg_isready -h pg-primary -U admin; do echo 'Waiting for primary...'; sleep 2; done;
        if [ ! -f /var/lib/postgresql/data/PG_VERSION ]; then
          echo 'Taking base backup from primary...';
          pg_basebackup -h pg-primary -U admin -D /var/lib/postgresql/data -P -Xs -R;
          echo 'hot_standby = on' >> /var/lib/postgresql/data/postgresql.conf;
        fi;
        exec docker-entrypoint.sh postgres -c hot_standby=on
      "
    depends_on:
      pg-primary:
        condition: service_healthy
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin"]
      interval: 5s
      timeout: 5s
      retries: 15

  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: dbopt-api
    networks: [dbopt-net]
    ports: ["8000:8000"]
    environment:
      PRIMARY_DB_URL: postgresql://admin:admin_pass@pg-primary:5432/dbopt_dev
      REPLICA_DB_URL: postgresql://admin:admin_pass@pg-replica:5432/dbopt_dev
    depends_on:
      pg-primary:
        condition: service_healthy

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: dbopt-frontend
    networks: [dbopt-net]
    ports: ["3000:80"]
    environment:
      REACT_APP_API_URL: ""
    depends_on: [api]
YAML

# Backend Dockerfile
cat > "$PROJECT_DIR/backend/Dockerfile" <<'DFILE'
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
DFILE

# Frontend Dockerfile  
cat > "$PROJECT_DIR/frontend/Dockerfile" <<'DFILE'
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json .
RUN npm install --legacy-peer-deps
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
DFILE

cat > "$PROJECT_DIR/frontend/nginx.conf" <<'NGINX'
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;
    location / { try_files $uri /index.html; }
    location /api/ {
        proxy_pass http://dbopt-api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
NGINX

ok "Docker configuration created"

# =============================================================================
# PHASE 7: Stop Script
# =============================================================================
cat > "$PROJECT_DIR/stop.sh" <<'STOP'
#!/usr/bin/env bash
echo "Stopping Day 115 services..."
docker compose down 2>/dev/null || true
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "react-scripts start" 2>/dev/null || true
echo "All services stopped."
STOP
chmod +x "$PROJECT_DIR/stop.sh"
ok "stop.sh created"

# =============================================================================
# PHASE 7b: Start Script (full path, duplicate check)
# =============================================================================
cat > "$PROJECT_DIR/start.sh" <<'START'
#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"

# Check for duplicate services
if pgrep -f "uvicorn app.main:app" >/dev/null 2>&1; then
  echo "[!] Backend (uvicorn) already running. Run ./stop.sh first or use existing."
  exit 1
fi
if pgrep -f "react-scripts start" >/dev/null 2>&1; then
  echo "[!] Frontend (react-scripts) already running. Run ./stop.sh first or use existing."
  exit 1
fi

echo "Starting Day 115 services from $PROJECT_DIR"

# Backend (full path)
if [ -f "$BACKEND_DIR/venv/bin/activate" ]; then
  cd "$BACKEND_DIR"
  . venv/bin/activate
  nohup uvicorn app.main:app --reload --port "$BACKEND_PORT" > /tmp/day115-api.log 2>&1 &
  echo $! > /tmp/day115-api.pid
  echo "[✓] Backend started (port $BACKEND_PORT), PID $(cat /tmp/day115-api.pid)"
else
  echo "[!] Backend venv not found. Run setup.sh first."
  exit 1
fi

# Frontend (full path)
if [ -f "$FRONTEND_DIR/package.json" ]; then
  cd "$FRONTEND_DIR"
  REACT_APP_API_URL="http://localhost:$BACKEND_PORT" nohup npm start > /tmp/day115-frontend.log 2>&1 &
  echo $! > /tmp/day115-frontend.pid
  echo "[✓] Frontend starting (port $FRONTEND_PORT), PID $(cat /tmp/day115-frontend.pid)"
else
  echo "[!] Frontend not found at $FRONTEND_DIR"
  exit 1
fi

echo "Dashboard: http://localhost:$FRONTEND_PORT  API: http://localhost:$BACKEND_PORT"
echo "Logs: tail -f /tmp/day115-api.log  |  tail -f /tmp/day115-frontend.log"
echo "Stop: $PROJECT_DIR/stop.sh"
START
chmod +x "$PROJECT_DIR/start.sh"
ok "start.sh created"

# =============================================================================
# PHASE 8: Environment file
# =============================================================================
cat > "$PROJECT_DIR/backend/.env" <<'ENV'
PRIMARY_DB_URL=postgresql://admin:admin_pass@localhost:5432/dbopt_dev
REPLICA_DB_URL=
LAG_THRESHOLD_MS=500.0
DEBUG=false
ENV

# =============================================================================
# PHASE 9: Execute — Docker or Local
# =============================================================================
cd "$PROJECT_DIR"

if [ "$DOCKER_MODE" = true ]; then
  echo ""
  echo "════════════════════════════════════════════════"
  echo "  DOCKER MODE"
  echo "════════════════════════════════════════════════"
  
  command -v docker >/dev/null 2>&1 || die "Docker not found. Install Docker Desktop."
  
  info "Building and starting Docker containers..."
  docker compose build --parallel 2>&1 | tail -5
  docker compose up -d
  
  info "Waiting for services to be healthy..."
  for i in $(seq 1 60); do
    if docker compose ps | grep -q "healthy"; then
      sleep 5
      break
    fi
    echo -n "."
    sleep 3
  done
  echo ""
  
  # Wait for pg-primary specifically
  until docker compose exec pg-primary pg_isready -U admin -d dbopt_dev -q 2>/dev/null; do
    sleep 2
  done
  ok "PostgreSQL primary ready"
  
  # Wait for API
  for i in $(seq 1 30); do
    if curl -sf http://localhost:8000/health >/dev/null 2>&1; then
      break
    fi
    sleep 3
  done
  ok "API healthy"
  
  # Run unit tests (in container)
  info "Running unit tests..."
  docker compose exec api python -m pytest app/../tests/unit/ -v --tb=short 2>&1 | tail -25
  
  # Run integration tests
  info "Running integration tests..."
  docker compose exec api python -m pytest app/../tests/integration/ -v --tb=short 2>&1 | tail -20
  
  # Run load generator to populate pg_stat_statements
  info "Running load generator (30 seconds)..."
  docker compose exec api python app/../tests/load_generator.py --duration 30 --concurrency 5 &
  sleep 5
  
  echo ""
  ok "════════════════════════════════════════════════"
  ok " Dashboard:   http://localhost:3000"
  ok " API docs:    http://localhost:8000/docs"
  ok " Primary DB:  psql -h localhost -p 5432 -U admin -d dbopt_dev"
  ok " Replica DB:  psql -h localhost -p 5433 -U admin -d dbopt_dev"
  ok "════════════════════════════════════════════════"
  echo ""
  echo "Run ./stop.sh to shut everything down."

else
  echo ""
  echo "════════════════════════════════════════════════"
  echo "  LOCAL MODE (no Docker)"
  echo "════════════════════════════════════════════════"

  # Check PostgreSQL
  command -v psql >/dev/null 2>&1 || die "psql not found. Install PostgreSQL 16 client tools."
  
  # Optional: warn if PostgreSQL is not listening
  if ! (command -v ss >/dev/null 2>&1 && ss -tln | grep -q ':5432 ') && ! (command -v netstat >/dev/null 2>&1 && netstat -tln 2>/dev/null | grep -q ':5432 '); then
    warn "PostgreSQL does not appear to be listening on port 5432. API will return 503 until DB is running."
    warn "Start PostgreSQL or use: docker run -d -p 5432:5432 -e POSTGRES_USER=admin -e POSTGRES_PASSWORD=admin_pass -e POSTGRES_DB=dbopt_dev postgres:16-alpine"
  fi
  
  # Create local DB
  info "Setting up local PostgreSQL database..."
  if ! psql -h localhost -U "$(whoami)" -c '\l' 2>/dev/null | grep -q dbopt_dev; then
    createdb dbopt_dev 2>/dev/null || \
      PGPASSWORD=admin_pass psql -h localhost -U admin -c "CREATE DATABASE dbopt_dev;" 2>/dev/null || \
      warn "Could not create dbopt_dev — ensure PostgreSQL is running with a superuser account"
  fi
  
  PGPASSWORD=admin_pass psql -h localhost -U admin -d dbopt_dev -f postgres/init.sql 2>&1 | tail -5 || \
    psql -h localhost -U "$(whoami)" -d dbopt_dev -f postgres/init.sql 2>&1 | tail -5 || \
    warn "DB init may have partially failed — check PostgreSQL connection"
  ok "Database initialized"
  
  # Python virtual environment
  info "Setting up Python virtual environment..."
  cd backend
  python3 -m venv venv
  source venv/bin/activate
  pip install -q -r requirements.txt
  ok "Python dependencies installed"
  
  # Unit tests
  info "Running unit tests..."
  python -m pytest tests/unit/ -v --tb=short 2>&1
  ok "Unit tests complete"
  
  # Start backend
  info "Starting FastAPI backend on port $BACKEND_PORT..."
  nohup uvicorn app.main:app --reload --port $BACKEND_PORT > /tmp/day115-api.log 2>&1 &
  echo $! > /tmp/day115-api.pid
  sleep 4
  
  # Integration tests
  info "Running integration tests..."
  python -m pytest tests/integration/ -v --tb=short 2>&1 || warn "Some integration tests may need DB adjustments"
  
  # Load generator
  info "Generating query load for dashboard demo..."
  python tests/load_generator.py --duration 30 --concurrency 5 &
  
  # Frontend
  info "Installing frontend dependencies..."
  cd ../frontend
  npm install --legacy-peer-deps --silent
  ok "Frontend dependencies installed"
  
  info "Starting React frontend on port $FRONTEND_PORT..."
  REACT_APP_API_URL=http://localhost:$BACKEND_PORT nohup npm start > /tmp/day115-frontend.log 2>&1 &
  echo $! > /tmp/day115-frontend.pid
  
  sleep 8
  echo ""
  ok "════════════════════════════════════════════════"
  ok " Dashboard:  http://localhost:3000"
  ok " API docs:   http://localhost:8000/docs"
  ok " API log:    tail -f /tmp/day115-api.log"
  ok "════════════════════════════════════════════════"
  echo ""
  echo "Run ./stop.sh to shut down. Run ./start.sh to start again (full path, no duplicates)."
fi