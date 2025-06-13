import React, { useState, useEffect } from 'react';
import { getHealthStatus } from '../services/api';

const HealthDashboard = () => {
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchHealthData = async () => {
    try {
      const data = await getHealthStatus();
      setHealthData(data);
      setError(null);
      setLastUpdated(new Date());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealthData();
    const interval = setInterval(fetchHealthData, 5000); // Refresh every 5 seconds
    
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status) => {
    return status === 'healthy' || status === 'connected' ? '#4CAF50' : '#f44336';
  };

  if (loading) return <div className="loading">Loading health data...</div>;

  return (
    <div className="health-dashboard">
      <h2>System Health Dashboard</h2>
      
      {lastUpdated && (
        <p className="last-updated">
          Last updated: {lastUpdated.toLocaleTimeString()}
        </p>
      )}

      {error && (
        <div className="error-message">
          Error: {error}
        </div>
      )}

      {healthData && (
        <div className="health-grid">
          <div className="health-card">
            <h3>Overall Status</h3>
            <div 
              className="status-indicator"
              style={{ backgroundColor: getStatusColor(healthData.status) }}
            >
              {healthData.status.toUpperCase()}
            </div>
            <p>Uptime: {Math.floor(healthData.uptime_seconds / 60)} minutes</p>
          </div>

          <div className="health-card">
            <h3>System Resources</h3>
            <div className="metric">
              <span>Memory Usage:</span>
              <span>{healthData.system.memory_used_percent.toFixed(1)}%</span>
            </div>
            <div className="metric">
              <span>CPU Usage:</span>
              <span>{healthData.system.cpu_percent.toFixed(1)}%</span>
            </div>
            <div className="metric">
              <span>Available Memory:</span>
              <span>{healthData.system.memory_available_mb} MB</span>
            </div>
          </div>

          <div className="health-card">
            <h3>Application Metrics</h3>
            <div className="metric">
              <span>Total Requests:</span>
              <span>{healthData.application.request_count}</span>
            </div>
            <div className="metric">
              <span>Hello Requests:</span>
              <span>{healthData.application.hello_count}</span>
            </div>
          </div>

          <div className="health-card">
            <h3>Dependencies</h3>
            {Object.entries(healthData.dependencies).map(([name, info]) => (
              <div key={name} className="dependency">
                <span>{name}:</span>
                <span 
                  style={{ color: getStatusColor(info.status) }}
                  className="dependency-status"
                >
                  {info.status}
                  {info.response_time_ms && ` (${info.response_time_ms}ms)`}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default HealthDashboard;
