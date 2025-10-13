import React from 'react';

const AlertStats = ({ stats }) => {
  return (
    <div className="stats-grid">
      <div className="stat-card">
        <div className="stat-number" style={{color: '#dc2626'}}>{stats.critical || 0}</div>
        <div className="stat-label">Critical</div>
      </div>
      <div className="stat-card">
        <div className="stat-number" style={{color: '#d97706'}}>{stats.warning || 0}</div>
        <div className="stat-label">Warnings</div>
      </div>
      <div className="stat-card">
        <div className="stat-number" style={{color: '#059669'}}>{stats.active || 0}</div>
        <div className="stat-label">Active</div>
      </div>
      <div className="stat-card">
        <div className="stat-number">{stats.total || 0}</div>
        <div className="stat-label">Total</div>
      </div>
    </div>
  );
};

export default AlertStats;
