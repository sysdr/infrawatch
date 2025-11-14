import React, { useState, useEffect, useRef } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './App.css';

const API_URL = 'http://localhost:8000';
const WS_URL = 'ws://localhost:8000';

function App() {
  const [clientId] = useState(`client-${Math.random().toString(36).substr(2, 9)}`);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [events, setEvents] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [messageText, setMessageText] = useState('');
  const [conflictLog, setConflictLog] = useState([]);
  const [performanceData, setPerformanceData] = useState([]);
  
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttemptsRef = useRef(0);
  const isManualCloseRef = useRef(false);

  useEffect(() => {
    // Wait a bit for backend to be ready before connecting
    const initialDelay = setTimeout(() => {
      connectWebSocket();
    }, 1000);
    
    const metricsInterval = setInterval(fetchMetrics, 2000);
    
    return () => {
      clearTimeout(initialDelay);
      clearInterval(metricsInterval);
      isManualCloseRef.current = true;
      if (wsRef.current) {
        // Only close if WebSocket is actually open or connecting
        if (wsRef.current.readyState === WebSocket.OPEN || 
            wsRef.current.readyState === WebSocket.CONNECTING) {
          wsRef.current.close();
        }
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, []);

  const connectWebSocket = () => {
    // Don't connect if already connected or connecting
    if (wsRef.current) {
      const state = wsRef.current.readyState;
      if (state === WebSocket.OPEN || state === WebSocket.CONNECTING) {
        console.log('WebSocket already connected or connecting, skipping...');
        return;
      }
    }

    try {
      const ws = new WebSocket(`${WS_URL}/ws/${clientId}`);
      
      ws.onopen = () => {
        console.log('WebSocket connected');
        setConnectionStatus('connected');
        reconnectAttemptsRef.current = 0; // Reset reconnect attempts on successful connection
        setEvents(prev => [...prev, {
          id: Date.now(),
          type: 'system',
          message: 'Connected to server',
          timestamp: new Date().toISOString()
        }]);
      };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Received:', data);
        
        if (data.type === 'ack') {
          setEvents(prev => [...prev, {
            id: Date.now(),
            type: 'ack',
            message: 'Message acknowledged',
            timestamp: data.timestamp
          }].slice(-20));
          
          // Check for conflicts in acknowledgment
          if (data.conflict_detected) {
            setConflictLog(prev => [...prev, {
              id: Date.now(),
              message: `Conflict detected and resolved: v${data.version || 'N/A'}`,
              timestamp: data.timestamp
            }].slice(-10));
          }
        } else {
          setEvents(prev => [...prev, {
            id: data.id,
            type: data.type,
            message: JSON.stringify(data.payload),
            timestamp: data.timestamp,
            from: data.client_id
          }].slice(-20));
          
          // Check for conflicts in broadcast messages
          if (data.conflict_detected || (data.version && data.version > 1)) {
            setConflictLog(prev => [...prev, {
              id: Date.now(),
              message: `Conflict resolved: v${data.version || 'N/A'}`,
              timestamp: data.timestamp
            }].slice(-10));
          }
        }
        
        updatePerformanceData();
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('error');
        // Don't try to reconnect immediately on error, let onclose handle it
      };
      
      ws.onclose = (event) => {
        console.log('WebSocket disconnected', event.code, event.reason);
        setConnectionStatus('disconnected');
        
        // Only add disconnect message if it wasn't a manual close
        if (!isManualCloseRef.current) {
          setEvents(prev => [...prev, {
            id: Date.now(),
            type: 'system',
            message: 'Disconnected from server',
            timestamp: new Date().toISOString()
          }]);
        }
        
        // Only attempt reconnection if it wasn't a manual close and not a normal closure
        if (!isManualCloseRef.current && event.code !== 1000) {
          reconnectAttemptsRef.current += 1;
          // Exponential backoff: 1s, 2s, 4s, 8s, max 10s
          const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current - 1), 10000);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log(`Attempting to reconnect... (attempt ${reconnectAttemptsRef.current})`);
            connectWebSocket();
          }, delay);
        } else {
          // Reset on manual close
          isManualCloseRef.current = false;
        }
      };
      
      wsRef.current = ws;
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      setConnectionStatus('error');
      // Retry connection on error
      reconnectAttemptsRef.current += 1;
      const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current - 1), 10000);
      reconnectTimeoutRef.current = setTimeout(() => {
        console.log(`Retrying connection after error... (attempt ${reconnectAttemptsRef.current})`);
        connectWebSocket();
      }, delay);
    }
  };

  const fetchMetrics = async () => {
    try {
      const response = await fetch(`${API_URL}/metrics`);
      const data = await response.json();
      setMetrics(data);
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    }
  };

  const updatePerformanceData = () => {
    setPerformanceData(prev => {
      const newData = [...prev, {
        time: new Date().toLocaleTimeString(),
        events: events.length,
        latency: Math.random() * 50 + 10
      }];
      return newData.slice(-20);
    });
  };

  const sendMessage = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN && messageText.trim()) {
      const event = {
        type: 'message.sent',
        payload: {
          message: messageText,
          entity_id: 'chat-1',
          timestamp: new Date().toISOString()
        },
        version: Math.floor(Math.random() * 3) + 1  // Simulate version conflicts
      };
      
      wsRef.current.send(JSON.stringify(event));
      setMessageText('');
      
      setEvents(prev => [...prev, {
        id: Date.now(),
        type: 'sent',
        message: messageText,
        timestamp: new Date().toISOString()
      }].slice(-20));
    }
  };

  const triggerNotification = async () => {
    try {
      await fetch(`${API_URL}/api/events`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: 'notification.created',
          payload: {
            title: 'System Notification',
            message: 'This is a broadcast notification',
            entity_id: 'notif-1'
          }
        })
      });
    } catch (error) {
      console.error('Failed to trigger notification:', error);
    }
  };

  const simulateOffline = () => {
    isManualCloseRef.current = true;
    if (wsRef.current) {
      wsRef.current.close();
    }
    setEvents(prev => [...prev, {
      id: Date.now(),
      type: 'system',
      message: 'Simulating offline mode...',
      timestamp: new Date().toISOString()
    }]);
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <h1>Real-time API Dashboard</h1>
          <div className="connection-badge">
            <span className={`status-dot ${connectionStatus}`}></span>
            <span className="status-text">{connectionStatus}</span>
          </div>
        </div>
        <div className="client-info">Client ID: {clientId}</div>
      </header>

      <div className="container">
        <div className="grid">
          <div className="card">
            <h2>System Metrics</h2>
            {metrics && (
              <div className="metrics-grid">
                <div className="metric">
                  <div className="metric-value">{metrics.connections.active}</div>
                  <div className="metric-label">Active Connections</div>
                </div>
                <div className="metric">
                  <div className="metric-value">{metrics.events.total_sent}</div>
                  <div className="metric-label">Events Sent</div>
                </div>
                <div className="metric">
                  <div className="metric-value">{metrics.sync.conflicts_detected}</div>
                  <div className="metric-label">Conflicts Detected</div>
                </div>
                <div className="metric">
                  <div className="metric-value">{metrics.sync.conflicts_resolved}</div>
                  <div className="metric-label">Conflicts Resolved</div>
                </div>
              </div>
            )}
          </div>

          <div className="card">
            <h2>Performance Monitor</h2>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={performanceData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                <XAxis dataKey="time" stroke="#888" />
                <YAxis stroke="#888" />
                <Tooltip 
                  contentStyle={{ background: '#2a2a2a', border: '1px solid #444' }}
                />
                <Legend />
                <Line type="monotone" dataKey="latency" stroke="#14b8a6" name="Latency (ms)" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="grid">
          <div className="card">
            <h2>Send Event</h2>
            <div className="send-message">
              <input
                type="text"
                value={messageText}
                onChange={(e) => setMessageText(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Type a message..."
                className="message-input"
              />
              <button onClick={sendMessage} className="btn btn-primary">
                Send
              </button>
            </div>
            <div className="action-buttons">
              <button onClick={triggerNotification} className="btn btn-secondary">
                Trigger Notification
              </button>
              <button onClick={simulateOffline} className="btn btn-secondary">
                Simulate Offline
              </button>
            </div>
          </div>

          <div className="card">
            <h2>Conflict Resolution Log</h2>
            <div className="log-container">
              {conflictLog.length === 0 ? (
                <div className="empty-state">No conflicts detected</div>
              ) : (
                conflictLog.map((log) => (
                  <div key={log.id} className="log-entry conflict">
                    <span className="log-time">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </span>
                    <span className="log-message">{log.message}</span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        <div className="card">
          <h2>Event Stream</h2>
          <div className="event-stream">
            {events.length === 0 ? (
              <div className="empty-state">No events yet</div>
            ) : (
              events.map((event) => (
                <div key={event.id} className={`event-item ${event.type}`}>
                  <div className="event-header">
                    <span className="event-type">{event.type}</span>
                    <span className="event-time">
                      {new Date(event.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <div className="event-content">{event.message}</div>
                  {event.from && (
                    <div className="event-from">From: {event.from}</div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
