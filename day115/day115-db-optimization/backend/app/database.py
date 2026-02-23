import threading
from sqlalchemy import create_engine, text, pool
from .config import settings

class DatabaseRouter:
    def __init__(self):
        self._lock = threading.Lock()
        self._replica_lag_ms = 0.0

        self.primary_engine = create_engine(
            settings.primary_db_url,
            poolclass=pool.QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 5}
        )

        use_replica = bool(settings.replica_db_url)
        self.replica_engine = create_engine(
            settings.replica_db_url if use_replica else settings.primary_db_url,
            poolclass=pool.QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 5}
        ) if use_replica else None

        self._has_replica = use_replica

    @property
    def replica_lag_ms(self):
        with self._lock:
            return self._replica_lag_ms

    @replica_lag_ms.setter
    def replica_lag_ms(self, v):
        with self._lock:
            self._replica_lag_ms = v

    def get_read_engine(self):
        if self._has_replica and self.replica_lag_ms < settings.lag_threshold_ms:
            return self.replica_engine
        return self.primary_engine

    def get_write_engine(self):
        return self.primary_engine

    def update_replication_lag(self):
        try:
            with self.primary_engine.connect() as conn:
                row = conn.execute(text("""
                    SELECT COALESCE(
                        EXTRACT(EPOCH FROM MAX(write_lag)) * 1000, 0
                    ) AS lag_ms
                    FROM pg_stat_replication
                """)).fetchone()
                self.replica_lag_ms = float(row.lag_ms) if row else 0.0
        except Exception:
            self.replica_lag_ms = 0.0

router = DatabaseRouter()
