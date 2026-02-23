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
            s.schemaname,
            s.relname AS tablename,
            s.indexrelname AS indexname,
            s.idx_scan AS scans,
            s.idx_tup_read AS tuples_read,
            s.idx_tup_fetch AS tuples_fetched,
            pg_size_pretty(pg_relation_size(s.indexrelid)) AS index_size,
            pg_relation_size(s.indexrelid) AS index_size_bytes,
            CASE WHEN s.idx_scan = 0 THEN true ELSE false END AS unused,
            ROUND(
                100.0 * s.idx_scan / NULLIF(s.idx_scan + t.seq_scan, 0), 2
            ) AS hit_rate_pct
        FROM pg_stat_user_indexes s
        JOIN pg_stat_user_tables t ON t.schemaname = s.schemaname AND t.relname = s.relname
        WHERE s.schemaname = 'public'
        ORDER BY s.idx_scan ASC, pg_relation_size(s.indexrelid) DESC
    """)
    with router.get_read_engine().connect() as conn:
        rows = conn.execute(sql).mappings().all()
    return [dict(r) for r in rows]

def get_table_bloat():
    """Estimate table and index bloat."""
    sql = text("""
        SELECT
            schemaname,
            relname AS tablename,
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
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||relname)) AS total_size
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
            relname AS tablename,
            seq_scan,
            seq_tup_read,
            idx_scan,
            n_live_tup AS row_count,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||relname)) AS table_size
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
