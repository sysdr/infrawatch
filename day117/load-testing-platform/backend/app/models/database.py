from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Float, Integer, DateTime, Text
from datetime import datetime
from typing import Optional
from app.core.config import settings

engine = create_async_engine(settings.db_url, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class TestRun(Base):
    __tablename__ = "test_runs"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(32), default="idle")
    test_type: Mapped[str] = mapped_column(String(32))  # load|benchmark|stress
    target_url: Mapped[str] = mapped_column(String(512))
    users: Mapped[int] = mapped_column(Integer, default=10)
    spawn_rate: Mapped[float] = mapped_column(Float, default=1.0)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=60)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

class TestMetric(Base):
    __tablename__ = "test_metrics"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(64))
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    rps: Mapped[float] = mapped_column(Float, default=0)
    p50_ms: Mapped[float] = mapped_column(Float, default=0)
    p95_ms: Mapped[float] = mapped_column(Float, default=0)
    p99_ms: Mapped[float] = mapped_column(Float, default=0)
    error_rate: Mapped[float] = mapped_column(Float, default=0)
    active_users: Mapped[int] = mapped_column(Integer, default=0)
    cpu_percent: Mapped[float] = mapped_column(Float, default=0)
    memory_percent: Mapped[float] = mapped_column(Float, default=0)
    total_requests: Mapped[int] = mapped_column(Integer, default=0)
    failed_requests: Mapped[int] = mapped_column(Integer, default=0)

class BenchmarkResult(Base):
    __tablename__ = "benchmark_results"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(64))
    endpoint: Mapped[str] = mapped_column(String(255))
    method: Mapped[str] = mapped_column(String(10))
    p50_ms: Mapped[float] = mapped_column(Float)
    p95_ms: Mapped[float] = mapped_column(Float)
    p99_ms: Mapped[float] = mapped_column(Float)
    mean_ms: Mapped[float] = mapped_column(Float)
    throughput_rps: Mapped[float] = mapped_column(Float)
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    iterations: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class StressResult(Base):
    __tablename__ = "stress_results"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(64))
    max_rps_sustainable: Mapped[float] = mapped_column(Float)
    breakdown_rps: Mapped[float] = mapped_column(Float)
    error_threshold_percent: Mapped[float] = mapped_column(Float, default=5.0)
    breakdown_cpu: Mapped[float] = mapped_column(Float)
    breakdown_memory: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
