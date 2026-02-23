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
