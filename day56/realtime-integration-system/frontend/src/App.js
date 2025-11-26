import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useWebSocket } from './hooks/useWebSocket';
import { useReconnection } from './hooks/useReconnection';
import ConnectionStatus from './components/ConnectionStatus';
import SystemMetrics from './components/SystemMetrics';
import NotificationPanel from './components/NotificationPanel';
import AlertPanel from './components/AlertPanel';
import CircuitBreakerStatus from './components/CircuitBreakerStatus';
import './App.css';

function App() {
  // Use useRef to maintain stable clientId across renders
  const clientIdRef = useRef(null);
  if (!clientIdRef.current) {
    clientIdRef.current = `client_${Date.now()}`;
  }
  const clientId = clientIdRef.current;
  const [systemStatus, setSystemStatus] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [alerts, setAlerts] = useState([]);
  
  const { 
    isConnected, 
    connectionState, 
    sendMessage, 
    lastMessage 
  } = useWebSocket(`ws://localhost:8000/ws/${clientId}`);
  
  const { 
    reconnectAttempts, 
    isReconnecting 
  } = useReconnection(isConnected);

  const requestStatus = useCallback(() => {
    if (isConnected && sendMessage) {
      sendMessage({ type: 'get_status' });
    }
  }, [isConnected, sendMessage]);

  // Handle incoming messages
  useEffect(() => {
    if (lastMessage) {
      const data = lastMessage;
      
      switch (data.type) {
        case 'connected':
          console.log('Connected to server');
          requestStatus();
          break;
        
        case 'status':
          setSystemStatus(data);
          setMetrics(data.metrics);
          break;
        
        case 'notification_sent':
          setNotifications(prev => [data.result, ...prev].slice(0, 10));
          break;
        
        case 'alert_created':
          setAlerts(prev => [data.alert, ...prev].slice(0, 10));
          break;
        
        case 'heartbeat':
          // Update last heartbeat time
          break;
        
        case 'version_check':
          // Handle version check
          break;
        
        default:
          console.log('Unknown message type:', data.type);
      }
    }
  }, [lastMessage, requestStatus]);

  const sendNotification = useCallback(() => {
    if (isConnected && sendMessage) {
      sendMessage({
        type: 'send_notification',
        notification_data: {
          channel: 'email',
          priority: 'normal',
          message: 'Test notification from UI'
        }
      });
    } else {
      console.warn('Cannot send notification: WebSocket not connected');
    }
  }, [isConnected, sendMessage]);

  const createAlert = useCallback((severity) => {
    if (isConnected && sendMessage) {
      sendMessage({
        type: 'create_alert',
        alert_data: {
          severity,
          message: `Test ${severity} alert from UI`
        }
      });
    } else {
      console.warn('Cannot create alert: WebSocket not connected');
    }
  }, [isConnected, sendMessage]);

  // Auto-refresh status
  useEffect(() => {
    const interval = setInterval(() => {
      if (isConnected) {
        requestStatus();
      }
    }, 5000);
    
    return () => clearInterval(interval);
  }, [isConnected, requestStatus]);

  return (
    <div className="App">
      <header className="app-header">
        <h1>🔄 Real-time Integration System</h1>
        <ConnectionStatus 
          isConnected={isConnected}
          state={connectionState}
          reconnectAttempts={reconnectAttempts}
          isReconnecting={isReconnecting}
        />
      </header>

      <div className="dashboard">
        <div className="metrics-row">
          <SystemMetrics 
            metrics={metrics}
            connectionCount={systemStatus?.connections || 0}
          />
          
          <CircuitBreakerStatus 
            circuitBreakers={systemStatus?.circuit_breakers || {}}
          />
        </div>

        <div className="controls-panel">
          <h3>Control Panel</h3>
          {!isConnected && (
            <div style={{ 
              padding: '10px', 
              backgroundColor: '#fef3c7', 
              borderRadius: '4px', 
              marginBottom: '15px',
              color: '#92400e'
            }}>
              ⚠️ Waiting for WebSocket connection...
            </div>
          )}
          <div className="button-group">
            <button 
              onClick={(e) => {
                e.preventDefault();
                sendNotification();
              }} 
              disabled={!isConnected}
              title={!isConnected ? "Connect to WebSocket first" : "Send a test notification"}
            >
              📧 Send Notification
            </button>
            <button 
              onClick={(e) => {
                e.preventDefault();
                createAlert('info');
              }} 
              disabled={!isConnected}
              title={!isConnected ? "Connect to WebSocket first" : "Create an info alert"}
            >
              ℹ️ Info Alert
            </button>
            <button 
              onClick={(e) => {
                e.preventDefault();
                createAlert('high');
              }} 
              disabled={!isConnected}
              title={!isConnected ? "Connect to WebSocket first" : "Create a high priority alert"}
            >
              ⚠️ High Alert
            </button>
            <button 
              onClick={(e) => {
                e.preventDefault();
                createAlert('critical');
              }} 
              disabled={!isConnected}
              title={!isConnected ? "Connect to WebSocket first" : "Create a critical alert"}
            >
              🚨 Critical Alert
            </button>
            <button 
              onClick={(e) => {
                e.preventDefault();
                requestStatus();
              }} 
              disabled={!isConnected}
              title={!isConnected ? "Connect to WebSocket first" : "Refresh system status and metrics"}
            >
              🔄 Refresh Status
            </button>
          </div>
        </div>

        <div className="panels-row">
          <NotificationPanel notifications={notifications} />
          <AlertPanel alerts={alerts} />
        </div>
      </div>
    </div>
  );
}

export default App;
