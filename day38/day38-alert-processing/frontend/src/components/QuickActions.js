import React from 'react';
import { useAlerts } from '../services/AlertContext';

function QuickActions() {
  const { createTestAlert } = useAlerts();

  return (
    <div className="quick-actions">
      <h3>Quick Actions</h3>
      <div className="action-buttons">
        <button 
          className="btn btn-primary"
          onClick={createTestAlert}
        >
          Create Test Alert
        </button>
        <button className="btn btn-secondary">
          View All Alerts
        </button>
        <button className="btn btn-outline">
          Export Data
        </button>
      </div>
    </div>
  );
}

export default QuickActions;
