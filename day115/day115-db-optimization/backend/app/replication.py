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
