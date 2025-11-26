import React from 'react';

const ConnectionStatus = ({ isConnected, state, reconnectAttempts, isReconnecting }) => {
  const getStatusColor = () => {
    if (isConnected) return '#10b981';
    if (isReconnecting) return '#f59e0b';
    return '#ef4444';
  };

  const getStatusText = () => {
    if (isConnected) return 'Connected';
    if (isReconnecting) return `Reconnecting (${reconnectAttempts}/10)`;
    return 'Disconnected';
  };

  return (
    <div className="connection-status" style={{ 
      backgroundColor: getStatusColor(),
      color: 'white',
      padding: '10px 20px',
      borderRadius: '8px',
      display: 'inline-block'
    }}>
      <span style={{ marginRight: '8px' }}>
        {isConnected ? '🟢' : isReconnecting ? '🟡' : '🔴'}
      </span>
      <strong>{getStatusText()}</strong>
      <span style={{ marginLeft: '10px', fontSize: '0.9em' }}>
        {state}
      </span>
    </div>
  );
};

export default ConnectionStatus;
