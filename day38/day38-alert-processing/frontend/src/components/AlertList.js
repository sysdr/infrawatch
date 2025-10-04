import React from 'react';
import { useAlerts } from '../services/AlertContext';
import { Link } from 'react-router-dom';

function AlertList() {
  const { alerts, loading, acknowledgeAlert, resolveAlert } = useAlerts();

  const getSeverityColor = (severity) => {
    const colors = {
      LOW: '#2ECC71',
      MEDIUM: '#F39C12',
      HIGH: '#E67E22',
      CRITICAL: '#E74C3C'
    };
    return colors[severity] || '#95A5A6';
  };

  if (loading) return <div className="loading">Loading alerts...</div>;

  return (
    <div className="alert-list">
      <div className="page-header">
        <h2>Alert Management</h2>
        <p>View and manage all system alerts</p>
      </div>

      <div className="alert-table">
        <div className="table-header">
          <div>Alert</div>
          <div>Service</div>
          <div>Severity</div>
          <div>State</div>
          <div>Created</div>
          <div>Actions</div>
        </div>
        
        {alerts.map(alert => (
          <div key={alert.id} className="table-row">
            <div className="alert-title">
              <Link to={`/alerts/${alert.id}`}>{alert.title}</Link>
            </div>
            <div>{alert.service_name}</div>
            <div>
              <span 
                className="severity-badge"
                style={{ backgroundColor: getSeverityColor(alert.severity) }}
              >
                {alert.severity}
              </span>
            </div>
            <div>
              <span className={`state-badge ${alert.state.toLowerCase()}`}>
                {alert.state}
              </span>
            </div>
            <div>{new Date(alert.created_at).toLocaleString()}</div>
            <div className="actions">
              {alert.state === 'NEW' && (
                <button 
                  onClick={() => acknowledgeAlert(alert.id, 'Admin')}
                  className="btn-small btn-primary"
                >
                  Acknowledge
                </button>
              )}
              {alert.state === 'ACKNOWLEDGED' && (
                <button 
                  onClick={() => resolveAlert(alert.id, 'Admin')}
                  className="btn-small btn-success"
                >
                  Resolve
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default AlertList;
