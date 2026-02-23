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
-- 2026 partition so seed data (NOW() - random 365 days) never fails
CREATE TABLE IF NOT EXISTS audit_events_2026_01 PARTITION OF audit_events
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');

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
