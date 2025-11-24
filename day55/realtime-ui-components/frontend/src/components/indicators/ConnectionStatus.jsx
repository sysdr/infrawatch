import React from 'react';
import { useRealtime } from '../../contexts/RealtimeContext';
import { Wifi, WifiOff, RefreshCw } from 'lucide-react';

function ConnectionStatus() {
  const { connectionStatus, latency, lastUpdate, reconnect } = useRealtime();

  const getStatusConfig = () => {
    switch (connectionStatus) {
      case 'connected':
        return {
          icon: Wifi,
          color: '#10b981',
          text: 'Connected',
          detail: latency ? `${Math.round(latency)}ms latency` : ''
        };
      case 'connecting':
        return {
          icon: RefreshCw,
          color: '#f59e0b',
          text: 'Connecting...',
          detail: ''
        };
      case 'reconnecting':
        return {
          icon: RefreshCw,
          color: '#f59e0b',
          text: 'Reconnecting...',
          detail: 'Attempting to restore connection'
        };
      case 'offline':
        return {
          icon: WifiOff,
          color: '#ef4444',
          text: 'Offline',
          detail: 'No connection'
        };
      default:
        return {
          icon: WifiOff,
          color: '#6b7280',
          text: 'Unknown',
          detail: ''
        };
    }
  };

  const config = getStatusConfig();
  const Icon = config.icon;

  const formatLastUpdate = (timestamp) => {
    if (!timestamp) return 'Never';
    const diff = Date.now() - new Date(timestamp).getTime();
    if (diff < 1000) return 'Just now';
    if (diff < 60000) return `${Math.floor(diff / 1000)}s ago`;
    return `${Math.floor(diff / 60000)}m ago`;
  };

  return (
    <div className="connection-status">
      <div className="status-indicator" style={{ backgroundColor: config.color }}>
        <Icon size={16} className={connectionStatus === 'reconnecting' ? 'spinning' : ''} />
      </div>
      <div className="status-details">
        <div className="status-text">{config.text}</div>
        {config.detail && <div className="status-detail">{config.detail}</div>}
        <div className="status-update">Last: {formatLastUpdate(lastUpdate)}</div>
      </div>
      {connectionStatus === 'offline' && (
        <button onClick={reconnect} className="reconnect-btn">
          Retry
        </button>
      )}
    </div>
  );
}

export default ConnectionStatus;
