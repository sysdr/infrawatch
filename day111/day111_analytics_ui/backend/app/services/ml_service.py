import os
import json
import joblib
import numpy as np
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from app.models.analytics import MLModel, MetricSnapshot
from app.schemas.analytics import MLPredictResponse
from app.core.config import settings

FEATURE_NAMES = ["cpu_utilization", "memory_usage", "request_latency_ms",
                 "error_rate", "throughput_rps", "queue_depth"]

class MLService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model_dir = Path(settings.MODEL_DIR)
        self.model_dir.mkdir(parents=True, exist_ok=True)

    async def ensure_model_exists(self):
        """Train and register a model if none exists."""
        result = await self.db.execute(
            select(MLModel).where(MLModel.name == "infra_anomaly", MLModel.is_active == True)
        )
        existing = result.scalar_one_or_none()
        if existing and Path(existing.artifact_path).exists():
            return existing

        model = await self._train_model()
        return model

    async def _train_model(self) -> MLModel:
        """Train GradientBoostingClassifier on seeded metric data."""
        np.random.seed(42)
        n = 2000
        X = np.column_stack([
            np.random.normal(50, 15, n),   # cpu
            np.random.normal(62, 10, n),   # memory
            np.random.normal(120, 40, n),  # latency
            np.random.exponential(0.5, n), # error_rate
            np.random.normal(850, 150, n), # throughput
            np.random.exponential(15, n),  # queue_depth
        ])
        # Anomaly = high latency OR high error OR high queue
        y = ((X[:, 2] > 200) | (X[:, 3] > 1.5) | (X[:, 5] > 40)).astype(int)

        pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", GradientBoostingClassifier(n_estimators=100, max_depth=3,
                                               learning_rate=0.1, random_state=42))
        ])
        pipeline.fit(X, y)
        clf = pipeline.named_steps["clf"]

        artifact_path = str(self.model_dir / "infra_anomaly_v1.joblib")
        joblib.dump(pipeline, artifact_path)

        metrics = {
            "train_samples": n,
            "feature_importances": dict(zip(FEATURE_NAMES, clf.feature_importances_.tolist())),
            "anomaly_rate": float(y.mean()),
        }

        # Deactivate any existing
        result = await self.db.execute(select(MLModel).where(MLModel.name == "infra_anomaly"))
        for m in result.scalars().all():
            m.is_active = False

        ml_model = MLModel(
            name="infra_anomaly",
            version="1.0",
            artifact_path=artifact_path,
            metrics=metrics,
            features=FEATURE_NAMES,
            is_active=True,
        )
        self.db.add(ml_model)
        await self.db.commit()
        await self.db.refresh(ml_model)
        return ml_model

    async def predict(self, features: dict[str, float], model_name: str = "infra_anomaly") -> MLPredictResponse:
        result = await self.db.execute(
            select(MLModel).where(MLModel.name == model_name, MLModel.is_active == True)
        )
        ml_model = result.scalar_one_or_none()
        if not ml_model or not Path(ml_model.artifact_path).exists():
            ml_model = await self._train_model()

        pipeline = joblib.load(ml_model.artifact_path)
        feature_vec = np.array([[features.get(f, 0.0) for f in FEATURE_NAMES]])
        proba = pipeline.predict_proba(feature_vec)[0]
        prediction_class = int(proba[1] >= 0.5)

        # Permutation importance
        baseline = float(proba[1])
        importance = {}
        for i, fname in enumerate(FEATURE_NAMES):
            shuffled = feature_vec.copy()
            shuffled[0, i] = np.random.normal(float(shuffled[0, i]), 5)
            delta = abs(baseline - float(pipeline.predict_proba(shuffled)[0][1]))
            importance[fname] = round(delta, 4)

        return MLPredictResponse(
            prediction="anomaly" if prediction_class == 1 else "normal",
            probability=round(float(proba[1]), 4),
            confidence=round(float(max(proba)), 4),
            feature_importance=importance,
            model_version=ml_model.version,
        )
