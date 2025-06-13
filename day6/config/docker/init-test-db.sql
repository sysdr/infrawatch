-- Test database initialization
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create test schemas
CREATE SCHEMA IF NOT EXISTS logs;
CREATE SCHEMA IF NOT EXISTS metrics;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA logs TO test_user;
GRANT ALL PRIVILEGES ON SCHEMA metrics TO test_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA logs TO test_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA metrics TO test_user;

-- Create test data function
CREATE OR REPLACE FUNCTION generate_test_data()
RETURNS void AS $$
BEGIN
    -- This function can be called to generate test data
    RAISE NOTICE 'Test database initialized successfully';
END;
$$ LANGUAGE plpgsql;

SELECT generate_test_data();
