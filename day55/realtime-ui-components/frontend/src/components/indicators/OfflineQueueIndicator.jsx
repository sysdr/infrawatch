import React from 'react';
import { useRealtime } from '../../contexts/RealtimeContext';
import { Clock, Activity, Wifi, Server, Zap } from 'lucide-react';

function OfflineQueueIndicator() {
  const { 
    offlineQueue, 
    connectionStatus, 
    latency, 
    lastUpdate,
    userCount,
    messageRate,
    data
  } = useRealtime();

  const formatTime = (timestamp) => {
    if (!timestamp) return 'Never';
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    if (diff < 1000) return 'Just now';
    if (diff < 60000) return `${Math.floor(diff / 1000)}s ago`;
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    return date.toLocaleTimeString();
  };

  const getLatencyColor = (latency) => {
    if (latency < 50) return '#10b981';
    if (latency < 100) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div className="system-status-container">
      <div className="status-grid">
        <div className="status-item">
          <div className="status-item-header">
            <Wifi size={20} color="#3b82f6" />
            <span className="status-item-label">Connection</span>
          </div>
          <div className="status-item-value">
            <span className={`status-badge status-${connectionStatus}`}>
              {connectionStatus.charAt(0).toUpperCase() + connectionStatus.slice(1)}
            </span>
          </div>
        </div>

        <div className="status-item">
          <div className="status-item-header">
            <Activity size={20} color={getLatencyColor(latency)} />
            <span className="status-item-label">Latency</span>
          </div>
          <div className="status-item-value">
            {latency > 0 ? `${Math.round(latency)}ms` : 'N/A'}
          </div>
        </div>

        <div className="status-item">
          <div className="status-item-header">
            <Server size={20} color="#8b5cf6" />
            <span className="status-item-label">Active Users</span>
          </div>
          <div className="status-item-value">{userCount.toLocaleString()}</div>
        </div>

        <div className="status-item">
          <div className="status-item-header">
            <Zap size={20} color="#f59e0b" />
            <span className="status-item-label">Message Rate</span>
          </div>
          <div className="status-item-value">{messageRate.toFixed(2)} msg/s</div>
        </div>
      </div>

      <div className="status-footer">
        <div className="status-meta">
          <Clock size={16} color="#6b7280" />
          <span>Last update: {formatTime(lastUpdate)}</span>
        </div>
        {offlineQueue.length > 0 && (
          <div className="queue-warning">
            <Clock size={16} color="#f59e0b" />
            <span>{offlineQueue.length} queued action{offlineQueue.length !== 1 ? 's' : ''}</span>
          </div>
        )}
      </div>
    </div>
  );
}

export default OfflineQueueIndicator;
