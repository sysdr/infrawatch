import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { SAMPLE_ALERTS, SAMPLE_ALERT_STATS } from '../sampleData';

function AlertDashboard({ ws, refreshTrigger, showDemoData }) {
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAlerts();
    fetchStats();
    const interval = setInterval(() => {
      fetchAlerts();
      fetchStats();
    }, 3000);
    return () => clearInterval(interval);
  }, [refreshTrigger]);

  const fetchAlerts = async () => {
    try {
      const response = await api.get('/api/alerts');
      const data = Array.isArray(response.data) ? response.data : [];
      setAlerts(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching alerts:', error);
      setAlerts([]);
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await api.get('/api/alerts/statistics?hours=24');
      setStats(response.data || {});
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const displayAlerts = (showDemoData && alerts.length === 0) ? SAMPLE_ALERTS : alerts;
  const displayStats = (showDemoData && alerts.length === 0) ? SAMPLE_ALERT_STATS : stats;

  const handleAcknowledge = async (alertId) => {
    try {
      await api.post(`/api/alerts/${alertId}/acknowledge`);
      fetchAlerts();
    } catch (error) {
      console.error('Error acknowledging alert:', error);
    }
  };

  const handleResolve = async (alertId) => {
    try {
      await api.post(`/api/alerts/${alertId}/resolve`);
      fetchAlerts();
    } catch (error) {
      console.error('Error resolving alert:', error);
    }
  };

  if (loading && !showDemoData) return <div className="loading">Loading alerts...</div>;

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h2>🔔 Alert Management</h2>
        <button className="refresh-button" onClick={fetchAlerts}>
          🔄 Refresh
        </button>
      </div>

      {showDemoData && alerts.length === 0 && (
        <p style={{ padding: '0.5rem 1rem', background: '#e0f2fe', borderRadius: '8px', marginBottom: '1rem', fontSize: '0.9rem' }}>
          📋 Sample data — Click <strong>Load Demo Data</strong> in the header to populate with real data.
        </p>
      )}
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Alerts (24h)</h3>
          <div className="value">{displayStats.total ?? stats.total ?? 0}</div>
        </div>
        <div className="stat-card">
          <h3>Active</h3>
          <div className="value">{displayStats.active ?? stats.active ?? 0}</div>
        </div>
        <div className="stat-card">
          <h3>Resolved</h3>
          <div className="value">{displayStats.resolved ?? stats.resolved ?? 0}</div>
        </div>
        <div className="stat-card">
          <h3>Critical</h3>
          <div className="value">{displayStats.by_severity?.critical ?? stats.by_severity?.critical ?? 0}</div>
        </div>
      </div>

      <table className="data-table">
        <thead>
          <tr>
            <th>Time</th>
            <th>Title</th>
            <th>Type</th>
            <th>Severity</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {displayAlerts.map(alert => (
            <tr key={alert.id}>
              <td>{new Date(alert.timestamp).toLocaleString()}</td>
              <td style={{maxWidth: '300px'}}>{alert.title}</td>
              <td>{alert.alert_type}</td>
              <td>
                <span className={`severity-badge severity-${alert.severity}`}>
                  {alert.severity}
                </span>
              </td>
              <td>{alert.status}</td>
              <td>
                {alert.status === 'active' && (
                  <button 
                    onClick={() => handleAcknowledge(alert.id)}
                    style={{padding: '0.5rem 1rem', marginRight: '0.5rem', cursor: 'pointer'}}
                  >
                    Acknowledge
                  </button>
                )}
                {alert.status !== 'resolved' && (
                  <button 
                    onClick={() => handleResolve(alert.id)}
                    style={{padding: '0.5rem 1rem', cursor: 'pointer'}}
                  >
                    Resolve
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default AlertDashboard;
