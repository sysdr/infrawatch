-- Initialize PostgreSQL with proper authentication
ALTER USER postgres PASSWORD 'password';
CREATE DATABASE metrics_db;
GRANT ALL PRIVILEGES ON DATABASE metrics_db TO postgres;
