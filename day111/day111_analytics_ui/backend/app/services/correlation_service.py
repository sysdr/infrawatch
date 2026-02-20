import numpy as np
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from scipy.stats import pearsonr, spearmanr
from app.models.analytics import MetricSnapshot
from app.schemas.analytics import CorrelationResponse

class CorrelationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def compute_matrix(self, metrics: list[str], hours: int = 6, method: str = "pearson") -> CorrelationResponse:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        series = {}
        for metric in metrics:
            r = await self.db.execute(
                select(MetricSnapshot.value, MetricSnapshot.recorded_at)
                .where(MetricSnapshot.metric_name == metric, MetricSnapshot.recorded_at >= cutoff)
                .order_by(MetricSnapshot.recorded_at)
            )
            rows = r.fetchall()
            series[metric] = [row.value for row in rows]

        # Align lengths
        min_len = min(len(v) for v in series.values()) if series else 0
        aligned = {m: np.array(v[-min_len:]) for m, v in series.items()}

        n = len(metrics)
        matrix = [[1.0] * n for _ in range(n)]
        labels = list(aligned.keys())

        for i in range(n):
            for j in range(i + 1, n):
                xi = aligned[labels[i]]
                xj = aligned[labels[j]]
                if len(xi) < 3:
                    coef = 0.0
                elif method == "spearman":
                    coef, _ = spearmanr(xi, xj)
                else:
                    coef, _ = pearsonr(xi, xj)
                coef = float(coef) if not np.isnan(coef) else 0.0
                matrix[i][j] = round(coef, 4)
                matrix[j][i] = round(coef, 4)

        return CorrelationResponse(
            matrix=matrix,
            labels=labels,
            method=method,
            computed_at=datetime.now(timezone.utc),
        )
