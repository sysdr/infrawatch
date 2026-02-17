import numpy as np
import pandas as pd
from scipy import stats
from scipy.signal import correlate
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from models.database import Metric, MetricData, Correlation, SessionLocal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CorrelationEngine:
    def __init__(self, window_minutes: int = 30, overlap_minutes: int = 5, threshold: float = 0.7):
        self.window_minutes = window_minutes
        self.overlap_minutes = overlap_minutes
        self.threshold = threshold
        self.db = SessionLocal()
    
    def fetch_metric_data(self, metric_id: int, lookback_minutes: int = 60) -> pd.Series:
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
    
    def compute_pearson_correlation(self, series_a: pd.Series, series_b: pd.Series) -> Tuple[float, float]:
        """Compute Pearson correlation coefficient and p-value"""
        if len(series_a) < 10 or len(series_b) < 10:
            return 0.0, 1.0
        
        # Align series by timestamp
        aligned = pd.concat([series_a, series_b], axis=1, join='inner')
        if aligned.shape[0] < 10:
            return 0.0, 1.0
        
        coefficient, p_value = stats.pearsonr(aligned.iloc[:, 0], aligned.iloc[:, 1])
        return coefficient, p_value
    
    def compute_spearman_correlation(self, series_a: pd.Series, series_b: pd.Series) -> Tuple[float, float]:
        """Compute Spearman correlation coefficient and p-value"""
        if len(series_a) < 10 or len(series_b) < 10:
            return 0.0, 1.0
        
        aligned = pd.concat([series_a, series_b], axis=1, join='inner')
        if aligned.shape[0] < 10:
            return 0.0, 1.0
        
        coefficient, p_value = stats.spearmanr(aligned.iloc[:, 0], aligned.iloc[:, 1])
        return coefficient, p_value
    
    def compute_lagged_correlation(self, series_a: pd.Series, series_b: pd.Series, 
                                   max_lag_minutes: int = 10) -> Tuple[float, int]:
        """Find best correlation with time lag"""
        if len(series_a) < 20 or len(series_b) < 20:
            return 0.0, 0
        
        aligned = pd.concat([series_a, series_b], axis=1, join='inner')
        if aligned.shape[0] < 20:
            return 0.0, 0
        
        values_a = aligned.iloc[:, 0].values
        values_b = aligned.iloc[:, 1].values
        
        # Normalize
        values_a = (values_a - np.mean(values_a)) / (np.std(values_a) + 1e-10)
        values_b = (values_b - np.mean(values_b)) / (np.std(values_b) + 1e-10)
        
        max_samples = min(max_lag_minutes, len(values_a) // 2)
        best_corr = 0.0
        best_lag = 0
        
        for lag in range(-max_samples, max_samples + 1):
            if lag == 0:
                corr = np.corrcoef(values_a, values_b)[0, 1]
            elif lag > 0:
                if len(values_a) > lag:
                    corr = np.corrcoef(values_a[:-lag], values_b[lag:])[0, 1]
                else:
                    continue
            else:
                pos_lag = abs(lag)
                if len(values_b) > pos_lag:
                    corr = np.corrcoef(values_a[pos_lag:], values_b[:-pos_lag])[0, 1]
                else:
                    continue
            
            if abs(corr) > abs(best_corr):
                best_corr = corr
                best_lag = lag
        
        # Convert sample lag to seconds (assuming 1-minute resolution)
        lag_seconds = best_lag * 60
        return best_corr, lag_seconds
    
    def detect_correlations(self) -> List[Dict]:
        """Main correlation detection loop"""
        logger.info("Starting correlation detection...")
        
        # Get all active metrics
        metrics = self.db.query(Metric).all()
        logger.info(f"Found {len(metrics)} metrics")
        
        detected_correlations = []
        
        # Compute correlations for all pairs
        for i, metric_a in enumerate(metrics):
            series_a = self.fetch_metric_data(metric_a.id, self.window_minutes)
            if series_a.empty:
                continue
            
            for metric_b in metrics[i+1:]:
                series_b = self.fetch_metric_data(metric_b.id, self.window_minutes)
                if series_b.empty:
                    continue
                
                # Compute Pearson
                pearson_coef, pearson_p = self.compute_pearson_correlation(series_a, series_b)
                
                # Compute Spearman
                spearman_coef, spearman_p = self.compute_spearman_correlation(series_a, series_b)
                
                # Choose best correlation
                if abs(pearson_coef) > abs(spearman_coef) and pearson_p < 0.05:
                    coef, p_val, corr_type = pearson_coef, pearson_p, "pearson"
                elif spearman_p < 0.05:
                    coef, p_val, corr_type = spearman_coef, spearman_p, "spearman"
                else:
                    continue
                
                # Check threshold
                if abs(coef) >= self.threshold:
                    # Compute time lag
                    lagged_coef, lag_seconds = self.compute_lagged_correlation(series_a, series_b)
                    
                    detected_correlations.append({
                        'metric_a_id': metric_a.id,
                        'metric_b_id': metric_b.id,
                        'metric_a_name': metric_a.name,
                        'metric_b_name': metric_b.name,
                        'coefficient': coef,
                        'correlation_type': corr_type,
                        'p_value': p_val,
                        'lag_seconds': lag_seconds,
                        'window_size': self.window_minutes
                    })
                    
                    logger.info(f"Detected: {metric_a.name} <-> {metric_b.name}, "
                               f"r={coef:.3f}, p={p_val:.4f}, lag={lag_seconds}s")
        
        # Save to database
        for corr_data in detected_correlations:
            # Check if correlation already exists
            existing = self.db.query(Correlation).filter(
                ((Correlation.metric_a_id == corr_data['metric_a_id']) & 
                 (Correlation.metric_b_id == corr_data['metric_b_id'])) |
                ((Correlation.metric_a_id == corr_data['metric_b_id']) & 
                 (Correlation.metric_b_id == corr_data['metric_a_id']))
            ).first()
            
            if existing:
                # Update existing
                existing.coefficient = corr_data['coefficient']
                existing.p_value = corr_data['p_value']
                existing.lag_seconds = corr_data['lag_seconds']
                existing.state = "active"
                existing.last_updated = datetime.utcnow()
            else:
                # Create new
                correlation = Correlation(
                    metric_a_id=corr_data['metric_a_id'],
                    metric_b_id=corr_data['metric_b_id'],
                    coefficient=corr_data['coefficient'],
                    correlation_type=corr_data['correlation_type'],
                    p_value=corr_data['p_value'],
                    lag_seconds=corr_data['lag_seconds'],
                    window_size=corr_data['window_size'],
                    state="active"
                )
                self.db.add(correlation)
        
        self.db.commit()
        logger.info(f"Saved {len(detected_correlations)} correlations")
        
        return detected_correlations
    
    def __del__(self):
        self.db.close()
