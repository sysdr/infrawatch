import React from 'react'

function AlertPanel({ alerts }) {
  if (alerts.length === 0) {
    return (
      <div className="alert-panel">
        <h3>Alerts</h3>
        <p className="no-alerts">No active alerts</p>
      </div>
    )
  }

  return (
    <div className="alert-panel">
      <h3>Recent Alerts ({alerts.length})</h3>
      <div className="alert-list">
        {alerts.slice(0, 5).map((alert) => (
          <div key={alert.id} className={`alert alert-${alert.severity}`}>
            <div className="alert-header">
              <span className="alert-severity">{alert.severity.toUpperCase()}</span>
              <span className="alert-time">
                {new Date(alert.timestamp * 1000).toLocaleTimeString()}
              </span>
            </div>
            <div className="alert-title">{alert.title}</div>
            <div className="alert-message">{alert.message}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default AlertPanel
