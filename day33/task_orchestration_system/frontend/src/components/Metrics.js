import React from 'react';

const Metrics = ({ metrics }) => {
  return (
    <div>
      <div className="wp-card">
        <div className="wp-card-header">
          <h2>Task Execution Metrics</h2>
        </div>
        <div className="wp-card-body">
          <div className="metrics-grid">
            <div className="metric-card">
              <span className="metric-value">{metrics.total_tasks || 0}</span>
              <div className="metric-label">Total Tasks Executed</div>
            </div>
            <div className="metric-card">
              <span className="metric-value">{metrics.completed_tasks || 0}</span>
              <div className="metric-label">Successful Tasks</div>
            </div>
            <div className="metric-card">
              <span className="metric-value">{metrics.failed_tasks || 0}</span>
              <div className="metric-label">Failed Tasks</div>
            </div>
            <div className="metric-card">
              <span className="metric-value">{metrics.success_rate || 0}%</span>
              <div className="metric-label">Success Rate</div>
            </div>
          </div>
        </div>
      </div>

      <div className="wp-card">
        <div className="wp-card-header">
          <h2>Recent Task History</h2>
        </div>
        <div className="wp-card-body">
          {metrics.recent_history && metrics.recent_history.length > 0 ? (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #ddd' }}>
                  <th style={{ textAlign: 'left', padding: '10px' }}>Timestamp</th>
                  <th style={{ textAlign: 'left', padding: '10px' }}>Task ID</th>
                  <th style={{ textAlign: 'left', padding: '10px' }}>Status</th>
                  <th style={{ textAlign: 'left', padding: '10px' }}>Execution Time</th>
                </tr>
              </thead>
              <tbody>
                {metrics.recent_history.map((record, index) => (
                  <tr key={index} style={{ borderBottom: '1px solid #eee' }}>
                    <td style={{ padding: '8px' }}>
                      {new Date(record.timestamp).toLocaleString()}
                    </td>
                    <td style={{ padding: '8px' }}>{record.task_id || 'N/A'}</td>
                    <td style={{ padding: '8px' }}>
                      <span className={`status-badge status-${record.status}`}>
                        {record.status}
                      </span>
                    </td>
                    <td style={{ padding: '8px' }}>
                      {record.execution_time ? `${record.execution_time}ms` : 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p>No task history available yet. Execute some workflows to see metrics.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Metrics;
