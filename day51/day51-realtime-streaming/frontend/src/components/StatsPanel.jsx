import React from 'react'

function StatsPanel({ stats, metricsCount }) {
  const streamStats = stats.stream_stats || {}
  
  return (
    <div className="stats-panel">
      <h3>Streaming Statistics</h3>
      <div className="stats-grid">
        <div className="stat-item">
          <div className="stat-label">Active Connections</div>
          <div className="stat-value">{streamStats.active_connections || 0}</div>
        </div>
        <div className="stat-item">
          <div className="stat-label">Subscriptions</div>
          <div className="stat-value">{streamStats.total_subscriptions || 0}</div>
        </div>
        <div className="stat-item">
          <div className="stat-label">Queued Messages</div>
          <div className="stat-value">{streamStats.queued_messages || 0}</div>
        </div>
        <div className="stat-item">
          <div className="stat-label">Metrics Collected</div>
          <div className="stat-value">{stats.metrics_collected || 0}</div>
        </div>
        <div className="stat-item">
          <div className="stat-label">Data Points</div>
          <div className="stat-value">{metricsCount}</div>
        </div>
        <div className="stat-item">
          <div className="stat-label">Topics</div>
          <div className="stat-value">{streamStats.topics || 0}</div>
        </div>
      </div>
    </div>
  )
}

export default StatsPanel
