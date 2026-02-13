import React, { useState, useEffect } from 'react';
import { dashboardAPI } from '../services/api';

export default function TrendAnalysis() {
  const [metrics, setMetrics] = useState([]);
  const [selectedMetric, setSelectedMetric] = useState('');
  const [trendData, setTrendData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    dashboardAPI.getMetrics()
      .then((data) => {
        setMetrics(data.metrics || []);
        if (data.metrics?.length) setSelectedMetric(data.metrics[0].name);
      })
      .catch(() => setMetrics([]));
  }, []);

  useEffect(() => {
    if (!selectedMetric) return;
    setLoading(true);
    setError(null);
    dashboardAPI.getTrendAnalysis(selectedMetric)
      .then(setTrendData)
      .catch((err) => {
        setError(err.message || 'Failed to load trend');
        setTrendData(null);
      })
      .finally(() => setLoading(false));
  }, [selectedMetric]);

  if (loading && !trendData) return <div className="loading">Analyzing trends...</div>;

  return (
    <div>
      <div className="controls">
        <div className="control-group">
          <label>Select metric</label>
          <select value={selectedMetric} onChange={(e) => setSelectedMetric(e.target.value)}>
            {(metrics || []).map((m) => (
              <option key={m.name} value={m.name}>{m.display_name}</option>
            ))}
          </select>
        </div>
      </div>

      {error && <div className="error">{error}</div>}

      {trendData?.status === 'insufficient_data' && (
        <div className="error">{trendData.message}</div>
      )}

      {trendData && trendData.status !== 'insufficient_data' && (
        <div className="chart-container">
          <div className="chart-header">
            <h3>Trend analysis: {selectedMetric}</h3>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem' }}>
            <div className="comparison-item">
              <div className="comparison-label">Trend</div>
              <div className="comparison-value" style={{ color: trendData.trend_direction === 'up' ? '#10b981' : trendData.trend_direction === 'down' ? '#ef4444' : '#6b7280' }}>
                {trendData.trend_direction === 'up' ? '↑' : trendData.trend_direction === 'down' ? '↓' : '→'} {String(trendData.trend_direction).toUpperCase()}
              </div>
            </div>
            <div className="comparison-item">
              <div className="comparison-label">Current value</div>
              <div className="comparison-value">{Number(trendData.current_value).toFixed(2)}</div>
            </div>
            <div className="comparison-item">
              <div className="comparison-label">7-day MA</div>
              <div className="comparison-value">{trendData.ma_7d != null ? Number(trendData.ma_7d).toFixed(2) : 'N/A'}</div>
            </div>
            <div className="comparison-item">
              <div className="comparison-label">30-day MA</div>
              <div className="comparison-value">{trendData.ma_30d != null ? Number(trendData.ma_30d).toFixed(2) : 'N/A'}</div>
            </div>
            <div className="comparison-item">
              <div className="comparison-label">Z-score</div>
              <div className="comparison-value" style={{ color: Math.abs(trendData.z_score) > 2 ? '#ef4444' : '#10b981' }}>
                {Number(trendData.z_score).toFixed(2)}
              </div>
            </div>
            <div className="comparison-item">
              <div className="comparison-label">Anomaly</div>
              <div className="comparison-value" style={{ color: trendData.is_anomaly ? '#ef4444' : '#10b981' }}>
                {trendData.is_anomaly ? '⚠ Yes' : '✓ No'}
              </div>
            </div>
          </div>
          <div style={{ marginTop: '1rem', padding: '1rem', background: '#f7fafc', borderRadius: 8, fontSize: '0.875rem' }}>
            <strong>Summary:</strong> Mean {Number(trendData.mean_value).toFixed(2)} · Std dev {Number(trendData.std_deviation).toFixed(2)} · Data points {trendData.data_points}
          </div>
        </div>
      )}
    </div>
  );
}
