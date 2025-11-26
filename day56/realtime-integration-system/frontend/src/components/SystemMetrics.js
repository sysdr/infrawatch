import React from 'react';

const SystemMetrics = ({ metrics, connectionCount }) => {
  if (!metrics) {
    return (
      <div className="metrics-card">
        <h3>System Metrics</h3>
        <p>Loading metrics...</p>
      </div>
    );
  }

  return (
    <div className="metrics-card">
      <h3>📊 System Metrics</h3>
      
      <div className="metric-item">
        <label>Active Connections:</label>
        <span className="metric-value">{connectionCount}</span>
      </div>

      {metrics.counters && Object.entries(metrics.counters).map(([key, value]) => (
        <div key={key} className="metric-item">
          <label>{key}:</label>
          <span className="metric-value">{value}</span>
        </div>
      ))}

      {metrics.latencies && (
        <div className="latency-section">
          <h4>Latency (ms)</h4>
          {Object.entries(metrics.latencies).map(([operation, latency]) => (
            <div key={operation} className="latency-item">
              <strong>{operation}:</strong>
              <div className="latency-stats">
                <span>Avg: {latency.avg}ms</span>
                <span>P95: {latency.p95}ms</span>
                <span>P99: {latency.p99}ms</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SystemMetrics;
