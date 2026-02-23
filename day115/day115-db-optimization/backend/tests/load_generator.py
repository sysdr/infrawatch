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
