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
