import React from 'react';

const AlertList = ({ alerts, loading, selectedAlerts, onSelectionChange }) => {
  if (loading) {
    return <div className="loading">Loading alerts...</div>;
  }

  const handleSelectAlert = (alertId) => {
    const newSelected = new Set(selectedAlerts);
    if (newSelected.has(alertId)) {
      newSelected.delete(alertId);
    } else {
      newSelected.add(alertId);
    }
    onSelectionChange(newSelected);
  };

  return (
    <div className="alert-list">
      {alerts.map(alert => (
        <div key={alert.id} className={`alert-item ${alert.severity}`}>
          <input
            type="checkbox"
            checked={selectedAlerts.has(alert.id)}
            onChange={() => handleSelectAlert(alert.id)}
          />
          <div className="alert-content">
            <h3>{alert.title}</h3>
            <p>{alert.description}</p>
            <div className="alert-meta">
              <span className="severity">{alert.severity}</span>
              <span className="status">{alert.status}</span>
              <span className="timestamp">{new Date(alert.timestamp).toLocaleString()}</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default AlertList;
