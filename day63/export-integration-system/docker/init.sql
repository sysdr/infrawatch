-- Create sample metrics table for demo
CREATE TABLE IF NOT EXISTS metrics (
    id VARCHAR(36) PRIMARY KEY,
    metric_name VARCHAR(255) NOT NULL,
    value NUMERIC(10, 2) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    tags JSONB DEFAULT '{}'
);

-- Insert sample data
INSERT INTO metrics (id, metric_name, value, timestamp, tags) 
SELECT 
    gen_random_uuid()::VARCHAR,
    CASE (random() * 4)::INT
        WHEN 0 THEN 'cpu_usage'
        WHEN 1 THEN 'memory_usage'
        WHEN 2 THEN 'disk_io'
        WHEN 3 THEN 'network_throughput'
        ELSE 'response_time'
    END,
    (random() * 100)::NUMERIC(10, 2),
    NOW() - (random() * INTERVAL '30 days'),
    jsonb_build_object('host', 'server-' || (random() * 10)::INT, 'region', 'us-east-1')
FROM generate_series(1, 100000);

CREATE INDEX idx_metrics_timestamp ON metrics(timestamp);
CREATE INDEX idx_metrics_name ON metrics(metric_name);
