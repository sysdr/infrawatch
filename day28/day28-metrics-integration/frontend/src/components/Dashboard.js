import React, { useState } from 'react';
import { useMetrics, useHealthCheck } from '../hooks/useMetrics';
import MetricsChart from './MetricsChart';
import RealtimeMetrics from './RealtimeMetrics';
import MetricCreator from './MetricCreator';
import HealthIndicator from './HealthIndicator';
import { Activity, BarChart3, Plus, Wifi, WifiOff } from 'lucide-react';
import './Dashboard.css';

const Dashboard = () => {
  const { 
    metrics, 
    realtimeMetrics, 
    loading, 
    error, 
    connected, 
    queryMetrics, 
    createMetric 
  } = useMetrics();
  
  const { health } = useHealthCheck();
  const [activeTab, setActiveTab] = useState('overview');
  const [showCreator, setShowCreator] = useState(false);

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'realtime', label: 'Real-time', icon: Activity },
    { id: 'historical', label: 'Historical', icon: BarChart3 }
  ];

  const handleMetricCreated = async (metric) => {
    try {
      await createMetric(metric);
      setShowCreator(false);
    } catch (err) {
      console.error('Failed to create metric:', err);
    }
  };

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-content">
          <h1>Metrics Dashboard</h1>
          <div className="header-actions">
            <HealthIndicator health={health} />
            <div className="connection-status">
              {connected ? (
                <Wifi className="icon connected" size={20} />
              ) : (
                <WifiOff className="icon disconnected" size={20} />
              )}
              <span>{connected ? 'Live' : 'Offline'}</span>
            </div>
            <button 
              className="btn btn-primary"
              onClick={() => setShowCreator(true)}
            >
              <Plus size={16} />
              Add Metric
            </button>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="dashboard-nav">
        <div className="nav-tabs">
          {tabs.map(tab => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                className={`nav-tab ${activeTab === tab.id ? 'active' : ''}`}
                onClick={() => setActiveTab(tab.id)}
              >
                <Icon size={16} />
                {tab.label}
              </button>
            );
          })}
        </div>
      </nav>

      {/* Main Content */}
      <main className="dashboard-main">
        {error && (
          <div className="alert alert-error">
            <strong>Error:</strong> {error}
          </div>
        )}

        {activeTab === 'overview' && (
          <div className="overview-grid">
            <div className="card">
              <h3>System Overview</h3>
              <div className="stats-grid">
                <div className="stat">
                  <div className="stat-value">{Object.keys(realtimeMetrics).length}</div>
                  <div className="stat-label">Active Metrics</div>
                </div>
                <div className="stat">
                  <div className="stat-value">{metrics.length}</div>
                  <div className="stat-label">Historical Records</div>
                </div>
                <div className="stat">
                  <div className="stat-value">{connected ? 'Live' : 'Offline'}</div>
                  <div className="stat-label">Connection Status</div>
                </div>
              </div>
            </div>
            
            <div className="card">
              <h3>Recent Activity</h3>
              <RealtimeMetrics metrics={realtimeMetrics} limit={5} />
            </div>
          </div>
        )}

        {activeTab === 'realtime' && (
          <div className="realtime-view">
            <div className="card">
              <h3>Real-time Metrics</h3>
              <RealtimeMetrics metrics={realtimeMetrics} />
            </div>
          </div>
        )}

        {activeTab === 'historical' && (
          <div className="historical-view">
            <div className="card">
              <h3>Historical Data</h3>
              {loading ? (
                <div className="loading">Loading metrics...</div>
              ) : (
                <MetricsChart metrics={metrics} />
              )}
            </div>
          </div>
        )}
      </main>

      {/* Metric Creator Modal */}
      {showCreator && (
        <MetricCreator
          onSubmit={handleMetricCreated}
          onCancel={() => setShowCreator(false)}
        />
      )}
    </div>
  );
};

export default Dashboard;
