import React from 'react';
import { useAlerts } from '../services/AlertContext';
import AlertStats from './AlertStats';
import RecentAlerts from './RecentAlerts';
import QuickActions from './QuickActions';

function Dashboard() {
  const { stats, alerts, loading } = useAlerts();

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Alert Processing Dashboard</h1>
        <p>Monitor and manage your system alerts in real-time</p>
      </div>
      
      <div className="dashboard-grid">
        <div className="dashboard-section">
          <AlertStats stats={stats} />
        </div>
        
        <div className="dashboard-section">
          <QuickActions />
        </div>
        
        <div className="dashboard-section full-width">
          <RecentAlerts alerts={alerts.slice(0, 10)} />
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
