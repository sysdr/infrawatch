import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { SAMPLE_TRENDS } from '../sampleData';

function TrendDashboard({ ws, refreshTrigger, showDemoData }) {
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTrends();
    const interval = setInterval(fetchTrends, 3000);
    return () => clearInterval(interval);
  }, [refreshTrigger]);

  const fetchTrends = async () => {
    try {
      const response = await api.get('/api/trends?hours=24');
      const data = Array.isArray(response.data) ? response.data : [];
      setTrends(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching trends:', error);
      setTrends([]);
      setLoading(false);
    }
  };

  const displayTrends = (showDemoData && trends.length === 0) ? SAMPLE_TRENDS : trends;

  if (loading && !showDemoData) return <div className="loading">Loading trends...</div>;

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h2>📈 Trend Analysis</h2>
        <button className="refresh-button" onClick={fetchTrends}>
          🔄 Refresh
        </button>
      </div>

      {displayTrends.length === 0 ? (
        <div className="loading" style={{ padding: '2rem' }}>
          <p>No trend data yet. Values will appear after logs with metrics are analyzed.</p>
          <p>Go to <strong>Simulator</strong> tab and click &quot;Start Simulation&quot; to populate metrics.</p>
        </div>
      ) : (
      <>
        {showDemoData && trends.length === 0 && (
          <p style={{ padding: '0.5rem 1rem', background: '#e0f2fe', borderRadius: '8px', marginBottom: '1rem', fontSize: '0.9rem' }}>
            📋 Sample data — Click <strong>Load Demo Data</strong> in the header to populate with real data.
          </p>
        )}
      <table className="data-table">
        <thead>
          <tr>
            <th>Metric</th>
            <th>Direction</th>
            <th>Current (30min avg)</th>
            <th>Predicted (1h)</th>
            <th>Confidence</th>
          </tr>
        </thead>
        <tbody>
          {displayTrends.map((trend, idx) => (
            <tr key={idx}>
              <td><strong>{trend.metric_name}</strong></td>
              <td>
                {trend.trend_direction === 'up' && '📈 Up'}
                {trend.trend_direction === 'down' && '📉 Down'}
                {trend.trend_direction === 'stable' && '➡️ Stable'}
              </td>
              <td>{(trend.moving_average ?? 0).toFixed(2)}</td>
              <td>{(trend.predicted_value_1h ?? 0).toFixed(2)}</td>
              <td>±{(trend.confidence_interval ?? 0).toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      </>
      )}
    </div>
  );
}

export default TrendDashboard;
