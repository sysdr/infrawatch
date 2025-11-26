import React from 'react';

const AlertPanel = ({ alerts }) => {
  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return '#ef4444';
      case 'high': return '#f59e0b';
      case 'medium': return '#3b82f6';
      case 'low': return '#10b981';
      case 'info': return '#6b7280';
      default: return '#6b7280';
    }
  };

  return (
    <div className="panel-card">
      <h3>🚨 Recent Alerts</h3>
      
      <div className="items-list">
        {alerts.map((alert, index) => (
          <div key={index} className="item">
            <div className="item-header">
              <span className="item-id">{alert.alert_id}</span>
              <span 
                className="item-severity"
                style={{
                  backgroundColor: getSeverityColor(alert.severity),
                  color: 'white',
                  padding: '2px 8px',
                  borderRadius: '4px',
                  fontSize: '0.85em'
                }}
              >
                {alert.severity}
              </span>
            </div>
            <div className="item-message">{alert.message}</div>
            <div className="item-time">
              {new Date(alert.created_at).toLocaleTimeString()}
            </div>
          </div>
        ))}
        
        {alerts.length === 0 && (
          <p className="empty-state">No alerts yet</p>
        )}
      </div>
    </div>
  );
};

export default AlertPanel;
