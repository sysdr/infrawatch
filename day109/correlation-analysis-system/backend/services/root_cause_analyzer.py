import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Set
from datetime import datetime, timedelta
from models.database import Metric, MetricData, Correlation, CausalRelation, SessionLocal
import logging
from collections import defaultdict, deque

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RootCauseAnalyzer:
    def __init__(self, granger_max_lag: int = 5):
        self.granger_max_lag = granger_max_lag
        self.db = SessionLocal()
    
    def granger_causality_test(self, cause_series: pd.Series, effect_series: pd.Series, 
                                max_lag: int = 5) -> Tuple[float, int]:
        """
        Simplified Granger causality test
        Tests if past values of cause_series improve prediction of effect_series
        """
        if len(cause_series) < 20 or len(effect_series) < 20:
            return 0.0, 0
        
        # Align series
        aligned = pd.concat([cause_series, effect_series], axis=1, join='inner')
        if aligned.shape[0] < 20:
            return 0.0, 0
        
        cause_vals = aligned.iloc[:, 0].values
        effect_vals = aligned.iloc[:, 1].values
        
        best_score = 0.0
        best_lag = 0
        
        for lag in range(1, min(max_lag, len(effect_vals) // 4) + 1):
            # Restricted model: predict effect from its own past
            y_restricted = effect_vals[lag:]
            X_restricted = np.array([effect_vals[i:i-lag or None] for i in range(lag)]).T
            
            # Unrestricted model: add past of cause
            X_unrestricted = np.column_stack([
                X_restricted,
                cause_vals[:len(y_restricted)]
            ])
            
            # Simple linear regression and compute RSS
            try:
                # Restricted RSS
                beta_r = np.linalg.lstsq(X_restricted, y_restricted, rcond=None)[0]
                y_pred_r = X_restricted @ beta_r
                rss_r = np.sum((y_restricted - y_pred_r) ** 2)
                
                # Unrestricted RSS
                beta_u = np.linalg.lstsq(X_unrestricted, y_restricted, rcond=None)[0]
                y_pred_u = X_unrestricted @ beta_u
                rss_u = np.sum((y_restricted - y_pred_u) ** 2)
                
                # Improvement score
                if rss_r > 0:
                    score = (rss_r - rss_u) / rss_r
                    if score > best_score:
                        best_score = score
                        best_lag = lag
            except:
                continue
        
        return best_score, best_lag
    
    def build_causal_graph(self, lookback_minutes: int = 60) -> Dict[int, List[Tuple[int, float]]]:
        """
        Build directed causal graph from correlations using Granger causality
        Returns adjacency list: {cause_metric_id: [(effect_metric_id, confidence), ...]}
        """
        logger.info("Building causal graph...")
        
        # Get correlations (active, validating, or candidate so analysis can run)
        correlations = self.db.query(Correlation).filter(
            Correlation.state.in_(["active", "validating", "candidate"])
        ).all()
        
        causal_graph = defaultdict(list)
        
        for corr in correlations:
            # Fetch data for both metrics
            cause_series = self.fetch_metric_data(corr.metric_a_id, lookback_minutes)
            effect_series = self.fetch_metric_data(corr.metric_b_id, lookback_minutes)
            
            if cause_series.empty or effect_series.empty:
                continue
            
            # Test A -> B
            score_a_to_b, lag_a_to_b = self.granger_causality_test(
                cause_series, effect_series, self.granger_max_lag
            )
            
            # Test B -> A
            score_b_to_a, lag_b_to_a = self.granger_causality_test(
                effect_series, cause_series, self.granger_max_lag
            )
            
            # Determine causal direction
            if score_a_to_b > 0.1 and score_a_to_b > score_b_to_a:
                causal_graph[corr.metric_a_id].append((corr.metric_b_id, score_a_to_b))
                self.save_causal_relation(corr.metric_a_id, corr.metric_b_id, score_a_to_b, lag_a_to_b)
                logger.info(f"Causal: {corr.metric_a_id} -> {corr.metric_b_id}, score={score_a_to_b:.3f}")
            elif score_b_to_a > 0.1 and score_b_to_a > score_a_to_b:
                causal_graph[corr.metric_b_id].append((corr.metric_a_id, score_b_to_a))
                self.save_causal_relation(corr.metric_b_id, corr.metric_a_id, score_b_to_a, lag_b_to_a)
                logger.info(f"Causal: {corr.metric_b_id} -> {corr.metric_a_id}, score={score_b_to_a:.3f}")
        
        return dict(causal_graph)
    
    def fetch_metric_data(self, metric_id: int, lookback_minutes: int) -> pd.Series:
        """Fetch time-series data for a metric"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=lookback_minutes)
        
        data_points = self.db.query(MetricData).filter(
            MetricData.metric_id == metric_id,
            MetricData.timestamp >= cutoff_time
        ).order_by(MetricData.timestamp).all()
        
        if not data_points:
            return pd.Series(dtype=float)
        
        df = pd.DataFrame([
            {'timestamp': d.timestamp, 'value': d.value}
            for d in data_points
        ])
        
        df.set_index('timestamp', inplace=True)
        return df['value']
    
    def save_causal_relation(self, cause_id: int, effect_id: int, score: float, lag: int):
        """Save causal relation to database"""
        existing = self.db.query(CausalRelation).filter(
            CausalRelation.cause_metric_id == cause_id,
            CausalRelation.effect_metric_id == effect_id
        ).first()
        
        if existing:
            existing.granger_score = score
            existing.lag_seconds = lag * 60
        else:
            relation = CausalRelation(
                cause_metric_id=cause_id,
                effect_metric_id=effect_id,
                granger_score=score,
                confidence=min(score * 100, 100),
                lag_seconds=lag * 60
            )
            self.db.add(relation)
        
        self.db.commit()
    
    def find_root_causes(self, causal_graph: Dict[int, List[Tuple[int, float]]]) -> List[Dict]:
        """
        Identify root causes using topological analysis
        Root causes have many outgoing edges and few/no incoming edges
        """
        # Count incoming and outgoing edges
        outgoing_count = {metric_id: len(effects) for metric_id, effects in causal_graph.items()}
        incoming_count = defaultdict(int)
        
        for effects in causal_graph.values():
            for effect_id, _ in effects:
                incoming_count[effect_id] += 1
        
        # Root causes: high outgoing, low incoming
        root_causes = []
        for metric_id, out_count in outgoing_count.items():
            in_count = incoming_count.get(metric_id, 0)
            if out_count > 0:
                root_score = out_count / (in_count + 1)
                if root_score >= 1.5:  # At least 1.5x more outgoing than incoming
                    metric = self.db.query(Metric).filter(Metric.id == metric_id).first()
                    root_causes.append({
                        'metric_id': metric_id,
                        'metric_name': metric.name if metric else f"Metric_{metric_id}",
                        'outgoing_effects': out_count,
                        'incoming_causes': in_count,
                        'root_score': root_score
                    })
        
        # Sort by root score
        root_causes.sort(key=lambda x: x['root_score'], reverse=True)
        
        logger.info(f"Identified {len(root_causes)} root causes")
        return root_causes
    
    def __del__(self):
        self.db.close()
