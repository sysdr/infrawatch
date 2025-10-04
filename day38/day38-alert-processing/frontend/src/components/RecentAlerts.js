import React from 'react';
import { Link } from 'react-router-dom';

function RecentAlerts({ alerts }) {
  return (
    <div className="recent-alerts">
      <h3>Recent Alerts</h3>
      <div className="alert-list-simple">
        {alerts.map(alert => (
          <div key={alert.id} className="alert-item-simple">
            <div className="alert-info">
              <Link to={`/alerts/${alert.id}`} className="alert-title">
                {alert.title}
              </Link>
              <span className="alert-service">{alert.service_name}</span>
            </div>
            <div className="alert-meta">
              <span className={`severity-badge ${alert.severity.toLowerCase()}`}>
                {alert.severity}
              </span>
              <span className="alert-time">
                {new Date(alert.created_at).toLocaleTimeString()}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default RecentAlerts;
