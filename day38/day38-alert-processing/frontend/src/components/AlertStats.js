import React, { useState, useEffect } from 'react';
import AlertService from '../services/AlertService';

function AlertStats({ stats: propStats }) {
  const [stats, setStats] = useState(propStats || {});
  const [loading, setLoading] = useState(!propStats);
  const [error, setError] = useState(null);

  useEffect(() => {
    // If no stats prop provided, fetch them
    if (!propStats) {
      loadStats();
    }
  }, [propStats]);

  const loadStats = async () => {
    try {
      setLoading(true);
      setError(null);
      const statsData = await AlertService.getStats();
      setStats(statsData);
    } catch (err) {
      setError(err.message);
      console.error('Error loading stats:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="stats-section">
        <h3>Alert Statistics</h3>
        <div className="loading">Loading statistics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="stats-section">
        <h3>Alert Statistics</h3>
        <div className="error">
          <p>Error loading statistics: {error}</p>
          <button onClick={loadStats} className="retry-btn">Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="stats-section">
      <h3>Alert Statistics</h3>
      <div className="stats-grid">
        <div className="stat-card">
          <h4>By State</h4>
          {Object.entries(stats.states || {}).map(([state, count]) => (
            <div key={state} className="stat-item">
              <span>{state}:</span>
              <strong>{count}</strong>
            </div>
          ))}
        </div>
        <div className="stat-card">
          <h4>By Severity</h4>
          {Object.entries(stats.severities || {}).map(([severity, count]) => (
            <div key={severity} className="stat-item">
              <span>{severity}:</span>
              <strong>{count}</strong>
            </div>
          ))}
        </div>
        <div className="stat-card">
          <h4>Recent Activity</h4>
          <div className="stat-item">
            <span>Last 24h:</span>
            <strong>{stats.recent_24h || 0}</strong>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AlertStats;
