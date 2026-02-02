import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { SAMPLE_ANOMALIES } from '../sampleData';

function AnomalyDashboard({ ws, refreshTrigger, showDemoData }) {
  const [anomalies, setAnomalies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnomalies();
    const interval = setInterval(fetchAnomalies, 3000);
    return () => clearInterval(interval);
  }, [refreshTrigger]);

  const fetchAnomalies = async () => {
    try {
      const response = await api.get('/api/anomalies?hours=24');
      const data = Array.isArray(response.data) ? response.data : [];
      setAnomalies(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching anomalies:', error);
      setAnomalies([]);
      setLoading(false);
    }
  };

  const displayAnomalies = (showDemoData && anomalies.length === 0) ? SAMPLE_ANOMALIES : anomalies;

  if (loading && !showDemoData) return <div className="loading">Loading anomalies...</div>;

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h2>⚠️ Anomaly Detection</h2>
        <button className="refresh-button" onClick={fetchAnomalies}>
          🔄 Refresh
        </button>
      </div>

      {displayAnomalies.length === 0 ? (
        <div className="loading" style={{ padding: '2rem' }}>
          <p>No anomalies detected. Values update when metrics deviate from baseline.</p>
          <p>Run the <strong>Simulator</strong> with &quot;Error Scenarios&quot; or &quot;Anomalies&quot; to trigger detection.</p>
        </div>
      ) : (
      <>
        {showDemoData && anomalies.length === 0 && (
          <p style={{ padding: '0.5rem 1rem', background: '#e0f2fe', borderRadius: '8px', marginBottom: '1rem', fontSize: '0.9rem' }}>
            📋 Sample data — Click <strong>Load Demo Data</strong> in the header to populate with real data.
          </p>
        )}
      <table className="data-table">
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Metric</th>
            <th>Value</th>
            <th>Z-Score</th>
            <th>Type</th>
            <th>Severity</th>
          </tr>
        </thead>
        <tbody>
          {displayAnomalies.slice(0, 15).map(anomaly => (
            <tr key={anomaly.id}>
              <td>{new Date(anomaly.timestamp).toLocaleString()}</td>
              <td><strong>{anomaly.metric_name}</strong></td>
              <td>{(anomaly.metric_value ?? 0).toFixed(2)}</td>
              <td><strong>{(anomaly.z_score ?? 0).toFixed(2)}</strong></td>
              <td>{anomaly.anomaly_type}</td>
              <td>
                <span className={`severity-badge severity-${anomaly.severity}`}>
                  {anomaly.severity}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      </>
      )}
    </div>
  );
}

export default AnomalyDashboard;
