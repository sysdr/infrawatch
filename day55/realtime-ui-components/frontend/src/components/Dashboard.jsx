import React, { useState } from 'react';
import { useRealtime } from '../contexts/RealtimeContext';
import ConnectionStatus from './indicators/ConnectionStatus';
import LiveUserCount from './charts/LiveUserCount';
import MessageRateChart from './charts/MessageRateChart';
import OfflineQueueIndicator from './indicators/OfflineQueueIndicator';
import AutoRefreshControl from './controls/AutoRefreshControl';
import '../styles/dashboard.css';

function Dashboard() {
  const { connectionStatus } = useRealtime();
  const [autoRefresh, setAutoRefresh] = useState(true);

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Real-time UI Dashboard</h1>
        <div className="header-controls">
          <AutoRefreshControl enabled={autoRefresh} onToggle={setAutoRefresh} />
          <ConnectionStatus />
        </div>
      </header>

      <div className="dashboard-grid">
        <div className="dashboard-card">
          <h2>Active Users</h2>
          <LiveUserCount />
        </div>

        <div className="dashboard-card">
          <h2>Message Rate</h2>
          <MessageRateChart />
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="dashboard-card full-width">
          <h2>System Status</h2>
          <OfflineQueueIndicator />
        </div>
      </div>

      {connectionStatus === 'offline' && (
        <div className="offline-banner">
          You're currently offline. Actions will be queued and sent when connection is restored.
        </div>
      )}
    </div>
  );
}

export default Dashboard;
