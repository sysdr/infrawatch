"""Database connection and initialization"""
import asyncpg
import os
import aiosqlite
import json
from typing import Optional, Union, Any
from contextlib import asynccontextmanager

_db_pool: Optional[Union[asyncpg.Pool, aiosqlite.Connection]] = None
_use_sqlite = False

async def init_db():
    """Initialize database connection pool"""
    global _db_pool, _use_sqlite
    
    # Use environment variable or try PostgreSQL, fallback to SQLite
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        # Try PostgreSQL connections
        # Use environment variables for database credentials
        # Default credentials removed - use DATABASE_URL environment variable
        pg_urls = [
            'postgresql://postgres@localhost:5433/postgres',
            'postgresql://postgres@localhost:5432/postgres',
        ]
        
        database_url = None
        for url in pg_urls:
            try:
                test_conn = await asyncpg.connect(url, timeout=2)
                await test_conn.close()
                database_url = url
                break
            except:
                continue
    
    if database_url:
        try:
            _db_pool = await asyncpg.create_pool(
                database_url,
                min_size=2,
                max_size=10,
                timeout=5
            )
            _use_sqlite = False
            print(f"Connected to PostgreSQL: {database_url.split('@')[-1]}")
        except Exception as e:
            print(f"PostgreSQL connection failed: {e}, using SQLite fallback")
            _use_sqlite = True
            database_url = None
    
    if not database_url or _use_sqlite:
        # Use SQLite as fallback
        print("Using SQLite database (fallback mode)")
        _use_sqlite = True
        db_path = os.path.join(os.path.dirname(__file__), '../../security_monitoring.db')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        _db_pool = await aiosqlite.connect(db_path)
        await _db_pool.execute("PRAGMA journal_mode=WAL")
    
    # Create tables with appropriate SQL syntax
    if _use_sqlite:
        # SQLite syntax
        await _db_pool.execute("""
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT UNIQUE NOT NULL,
                event_type TEXT NOT NULL,
                user_id TEXT,
                ip_address TEXT,
                user_agent TEXT,
                action TEXT,
                resource TEXT,
                success INTEGER,
                timestamp TEXT NOT NULL,
                country TEXT,
                city TEXT,
                latitude REAL,
                longitude REAL,
                metadata TEXT,
                severity INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await _db_pool.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_timestamp 
            ON security_events(timestamp DESC)
        """)
        
        await _db_pool.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_user_id 
            ON security_events(user_id)
        """)
        
        await _db_pool.execute("""
            CREATE TABLE IF NOT EXISTS threats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                threat_id TEXT UNIQUE NOT NULL,
                event_id TEXT,
                user_id TEXT,
                ip_address TEXT,
                attack_type TEXT,
                severity INTEGER NOT NULL,
                anomalies TEXT,
                detected_at TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                automated_response INTEGER DEFAULT 0,
                response_actions TEXT,
                responded_at TEXT,
                resolved_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await _db_pool.execute("""
            CREATE INDEX IF NOT EXISTS idx_threats_severity 
            ON threats(severity DESC)
        """)
        
        await _db_pool.execute("""
            CREATE TABLE IF NOT EXISTS response_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                threat_id TEXT NOT NULL,
                response_level TEXT,
                actions TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await _db_pool.execute("""
            CREATE TABLE IF NOT EXISTS user_baselines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                baseline_type TEXT,
                baseline_data TEXT,
                calculated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                valid_until TEXT
            )
        """)
        
        await _db_pool.commit()
    else:
        # PostgreSQL syntax
        async with _db_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS security_events (
                    id SERIAL PRIMARY KEY,
                    event_id VARCHAR(255) UNIQUE NOT NULL,
                    event_type VARCHAR(100) NOT NULL,
                    user_id VARCHAR(255),
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    action VARCHAR(100),
                    resource VARCHAR(500),
                    success BOOLEAN,
                    timestamp TIMESTAMPTZ NOT NULL,
                    country VARCHAR(100),
                    city VARCHAR(100),
                    latitude FLOAT,
                    longitude FLOAT,
                    metadata JSONB,
                    severity INTEGER DEFAULT 0,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_timestamp 
                ON security_events(timestamp DESC)
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_user_id 
                ON security_events(user_id)
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS threats (
                    id SERIAL PRIMARY KEY,
                    threat_id VARCHAR(255) UNIQUE NOT NULL,
                    event_id VARCHAR(255),
                    user_id VARCHAR(255),
                    ip_address VARCHAR(45),
                    attack_type VARCHAR(100),
                    severity INTEGER NOT NULL,
                    anomalies JSONB,
                    detected_at TIMESTAMPTZ NOT NULL,
                    status VARCHAR(50) DEFAULT 'active',
                    automated_response BOOLEAN DEFAULT false,
                    response_actions JSONB,
                    responded_at TIMESTAMPTZ,
                    resolved_at TIMESTAMPTZ,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_threats_severity 
                ON threats(severity DESC)
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS response_actions (
                    id SERIAL PRIMARY KEY,
                    threat_id VARCHAR(255) NOT NULL,
                    response_level VARCHAR(50),
                    actions JSONB,
                    timestamp TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS user_baselines (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    baseline_type VARCHAR(100),
                    baseline_data JSONB,
                    calculated_at TIMESTAMPTZ DEFAULT NOW(),
                    valid_until TIMESTAMPTZ
                )
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_baselines_user_id 
                ON user_baselines(user_id)
            """)
    
    print("Database initialized successfully")

async def get_db():
    """Get database connection from pool"""
    if _db_pool is None:
        await init_db()
    return _db_pool

def is_sqlite():
    """Check if SQLite is being used"""
    return _use_sqlite

# Helper functions for database operations that work with both backends
async def execute_query(query: str, *args):
    """Execute a query (works with both PostgreSQL and SQLite)"""
    db = await get_db()
    if _use_sqlite:
        cursor = await db.execute(query, args)
        await db.commit()
        return cursor
    else:
        async with db.acquire() as conn:
            return await conn.execute(query, *args)

async def fetch_query(query: str, *args):
    """Fetch results from a query"""
    db = await get_db()
    global _use_sqlite
    if _use_sqlite:
        cursor = await db.execute(query, args)
        rows = await cursor.fetchall()
        # Convert to list of dicts
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        return [dict(zip(columns, row)) for row in rows]
    else:
        async with db.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]

async def fetchrow_query(query: str, *args):
    """Fetch a single row from a query"""
    db = await get_db()
    global _use_sqlite
    if _use_sqlite:
        cursor = await db.execute(query, args)
        row = await cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            return dict(zip(columns, row))
        return None
    else:
        async with db.acquire() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None
