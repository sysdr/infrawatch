import React, { useState, useEffect } from 'react';
import { dashboardAPI } from '../services/api';

export default function Comparison() {
  const [metrics, setMetrics] = useState([]);
  const [selectedMetric, setSelectedMetric] = useState('');
  const [mode, setMode] = useState('dimension');
  const [dimension, setDimension] = useState('product');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    dashboardAPI.getMetrics()
      .then((d) => {
        setMetrics(d.metrics || []);
        if (d.metrics?.length) setSelectedMetric(d.metrics[0].name);
      })
      .catch(() => setMetrics([]));
  }, []);

  const runCompare = () => {
    if (!selectedMetric) return;
    setLoading(true);
    setError(null);
    const promise = mode === 'dimension'
      ? dashboardAPI.compareByDimension(selectedMetric, dimension, 30)
      : dashboardAPI.comparePeriods(selectedMetric, 7, 7);
    promise
      .then(setData)
      .catch((err) => {
        setError(err.message || 'Comparison failed');
        setData(null);
      })
      .finally(() => setLoading(false));
  };

  return (
    <div>
      <div className="controls">
        <div className="control-group">
          <label>Metric</label>
          <select value={selectedMetric} onChange={(e) => setSelectedMetric(e.target.value)}>
            {(metrics || []).map((m) => (
              <option key={m.name} value={m.name}>{m.display_name}</option>
            ))}
          </select>
        </div>
        <div className="control-group">
          <label>Type</label>
          <select value={mode} onChange={(e) => setMode(e.target.value)}>
            <option value="dimension">By dimension</option>
            <option value="period">By period</option>
          </select>
        </div>
        {mode === 'dimension' && (
          <div className="control-group">
            <label>Dimension</label>
            <select value={dimension} onChange={(e) => setDimension(e.target.value)}>
              <option value="product">Product</option>
              <option value="region">Region</option>
            </select>
          </div>
        )}
        <div className="control-group">
          <label>&nbsp;</label>
          <button className="btn btn-primary" onClick={runCompare} disabled={loading}>
            {loading ? 'Comparing...' : 'Compare'}
          </button>
        </div>
      </div>

      {error && <div className="error">{error}</div>}
      {data?.status === 'insufficient_data' && <div className="error">{data.message}</div>}

      {mode === 'dimension' && data?.comparisons?.length > 0 && (
        <div className="chart-container">
          <div className="chart-header">
            <h3>By {dimension}</h3>
            <p>Overall mean: {Number(data.overall_mean).toFixed(2)}</p>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '1rem' }}>
            {data.comparisons.map((c, i) => (
              <div key={i} className="comparison-item">
                <div className="comparison-label">{c.dimension_value}</div>
                <div className="comparison-value">{Number(c.mean).toFixed(2)}</div>
                <div className="comparison-diff" style={{ color: c.vs_overall >= 0 ? '#10b981' : '#ef4444' }}>
                  {(c.vs_overall >= 0 ? '+' : '') + Number(c.vs_overall).toFixed(1)}% vs avg
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {mode === 'period' && data?.period1 && data?.period2 && (
        <div className="chart-container">
          <div className="chart-header">
            <h3>Period comparison</h3>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1.5rem' }}>
            <div className="comparison-item">
              <div className="comparison-label">Period 1 mean</div>
              <div className="comparison-value">{Number(data.period1.mean).toFixed(2)}</div>
              <div style={{ fontSize: '0.875rem', color: '#657786' }}>n = {data.period1.count}</div>
            </div>
            <div className="comparison-item">
              <div className="comparison-label">Period 2 mean</div>
              <div className="comparison-value">{Number(data.period2.mean).toFixed(2)}</div>
              <div style={{ fontSize: '0.875rem', color: '#657786' }}>n = {data.period2.count}</div>
            </div>
            <div className="comparison-item">
              <div className="comparison-label">Change</div>
              <div className="comparison-value" style={{ color: data.comparison.change_percentage >= 0 ? '#10b981' : '#ef4444' }}>
                {(data.comparison.change_percentage >= 0 ? '+' : '') + Number(data.comparison.change_percentage).toFixed(2)}%
              </div>
              <div style={{ fontSize: '0.875rem', color: '#657786' }}>
                {data.comparison.statistically_significant ? '✓ Significant' : 'Not significant'}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
