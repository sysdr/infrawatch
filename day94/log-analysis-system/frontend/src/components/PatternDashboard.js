import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { SAMPLE_PATTERNS } from '../sampleData';

function PatternDashboard({ ws, refreshTrigger, showDemoData }) {
  const [patterns, setPatterns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ total: 0, critical: 0, categories: {} });
  const [lastUpdated, setLastUpdated] = useState(null);

  useEffect(() => {
    fetchPatterns();
    const interval = setInterval(fetchPatterns, 3000); // Poll every 3s for real-time feel
    return () => clearInterval(interval);
  }, [refreshTrigger]);

  const fetchPatterns = async () => {
    try {
      const response = await api.get('/api/patterns?hours=24');
      const data = Array.isArray(response.data) ? response.data : [];
      setPatterns(data);

      const total = data.length;
      const critical = data.filter(p => p && p.is_critical).length;
      const categories = {};
      data.forEach(p => {
        if (p && p.category) categories[p.category] = (categories[p.category] || 0) + 1;
      });

      setStats({ total, critical, categories });
      setLastUpdated(new Date());
      setLoading(false);
    } catch (error) {
      console.error('Error fetching patterns:', error);
      setPatterns([]);
      setStats({ total: 0, critical: 0, categories: {} });
      setLoading(false);
    }
  };

  const displayPatterns = (showDemoData && patterns.length === 0) ? SAMPLE_PATTERNS : patterns;
  const displayStats = (showDemoData && patterns.length === 0)
    ? {
        total: SAMPLE_PATTERNS.length,
        critical: SAMPLE_PATTERNS.filter(p => p.is_critical).length,
        categories: SAMPLE_PATTERNS.reduce((acc, p) => {
          acc[p.category] = (acc[p.category] || 0) + 1;
          return acc;
        }, {}),
      }
    : stats;

  if (loading && !showDemoData) return <div className="loading">Loading patterns...</div>;

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h2>📊 Pattern Analysis</h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {lastUpdated && !showDemoData && (
            <span style={{ fontSize: '0.8rem', color: '#6b7280' }}>
              Last updated: {lastUpdated.toLocaleTimeString()}
            </span>
          )}
          <button className="refresh-button" onClick={fetchPatterns}>
            🔄 Refresh
          </button>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Patterns</h3>
          <div className="value">{displayStats.total}</div>
        </div>
        <div className="stat-card">
          <h3>Critical Patterns</h3>
          <div className="value">{displayStats.critical}</div>
        </div>
        <div className="stat-card">
          <h3>Top Category</h3>
          <div className="value" style={{fontSize: '1.2rem'}}>
            {Object.keys(displayStats.categories).length ? Object.keys(displayStats.categories)[0] : 'N/A'}
          </div>
        </div>
      </div>

      {displayPatterns.length === 0 ? (
        <div className="loading" style={{ padding: '2rem' }}>
          <p>No patterns yet. Run the <strong>Simulator</strong> and click &quot;Start Simulation&quot; to analyze logs.</p>
        </div>
      ) : (
      <>
        {showDemoData && patterns.length === 0 && (
          <p style={{ padding: '0.5rem 1rem', background: '#e0f2fe', borderRadius: '8px', marginBottom: '1rem', fontSize: '0.9rem' }}>
            📋 Sample data — Click <strong>Load Demo Data</strong> in the header to populate with real data from the backend.
          </p>
        )}
      <table className="data-table">
        <thead>
          <tr>
            <th>Pattern Template</th>
            <th>Category</th>
            <th>Severity</th>
            <th>Frequency</th>
            <th>Last Seen</th>
          </tr>
        </thead>
        <tbody>
          {displayPatterns.slice(0, 10).map(pattern => (
            <tr key={pattern.id}>
              <td style={{maxWidth: '400px', overflow: 'hidden', textOverflow: 'ellipsis'}}>
                {pattern.template}
              </td>
              <td>{pattern.category}</td>
              <td>
                <span className={`severity-badge severity-${pattern.severity}`}>
                  {pattern.severity}
                </span>
              </td>
              <td><strong>{pattern.frequency}</strong></td>
              <td>{new Date(pattern.last_seen).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
      </>
      )}
    </div>
  );
}

export default PatternDashboard;
