import React from 'react';

function WorkerStats({ workers }) {
  const queueLengths = workers.queue_lengths || {};
  const activeWorkers = workers.active_workers || 0;

  return (
    <div>
      <h3>🔧 Worker Statistics</h3>
      
      <div className="stat-grid">
        <div className="stat-item">
          <div className="stat-label">Active Workers</div>
          <div className="stat-value">{activeWorkers}</div>
        </div>
        
        <div className="stat-item">
          <div className="stat-label">Total Queued Tasks</div>
          <div className="stat-value">
            {Object.values(queueLengths).reduce((sum, count) => sum + count, 0)}
          </div>
        </div>
      </div>

      <div className="queue-stats">
        <h4>📋 Queue Status</h4>
        {Object.entries(queueLengths).map(([queueName, count]) => (
          <div key={queueName} className="queue-item">
            <span className="queue-name">{queueName}</span>
            <span className="queue-count">{count}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default WorkerStats;
