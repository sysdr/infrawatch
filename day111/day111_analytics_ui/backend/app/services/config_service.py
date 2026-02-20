from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.analytics import AnalyticsConfig
from app.schemas.analytics import ConfigUpdate

DEFAULT_CONFIGS = {
    "refresh_interval_seconds": 5,
    "default_time_window_hours": 6,
    "alert_thresholds": {
        "cpu_utilization": 85,
        "memory_usage": 90,
        "error_rate": 2.0,
        "request_latency_ms": 300,
    },
    "data_sources": [
        {"name": "Production DB", "type": "postgresql", "status": "healthy"},
        {"name": "Redis Cache", "type": "redis", "status": "healthy"},
        {"name": "Metrics Store", "type": "timeseries", "status": "healthy"},
    ],
    "ui_preferences": {"dark_mode": False, "compact_view": False, "show_sparklines": True},
}

class ConfigService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def seed_defaults(self):
        for key, value in DEFAULT_CONFIGS.items():
            result = await self.db.execute(select(AnalyticsConfig).where(AnalyticsConfig.key == key))
            existing = result.scalar_one_or_none()
            if not existing:
                self.db.add(AnalyticsConfig(key=key, value=value))
        await self.db.commit()

    async def get_all(self) -> dict:
        result = await self.db.execute(select(AnalyticsConfig))
        return {c.key: c.value for c in result.scalars().all()}

    async def update(self, update: ConfigUpdate) -> dict:
        result = await self.db.execute(select(AnalyticsConfig).where(AnalyticsConfig.key == update.key))
        config = result.scalar_one_or_none()
        if config:
            config.value = update.value
        else:
            self.db.add(AnalyticsConfig(key=update.key, value=update.value))
        await self.db.commit()
        return {"key": update.key, "value": update.value}
