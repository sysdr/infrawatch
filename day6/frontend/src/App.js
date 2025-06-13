import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [newLog, setNewLog] = useState({
    message: '',
    level: 'INFO',
    source: '',
  });

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/logs`);
      if (!response.ok) {
        throw new Error('Failed to fetch logs');
      }
      const data = await response.json();
      setLogs(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const createLog = async (e) => {
    e.preventDefault();
    
    if (!newLog.message.trim()) {
      alert('Message is required');
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/logs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newLog),
      });

      if (!response.ok) {
        throw new Error('Failed to create log');
      }

      const createdLog = await response.json();
      setLogs([createdLog, ...logs]);
      setNewLog({ message: '', level: 'INFO', source: '' });
      
      // Show success message
      alert('Log created successfully');
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  const getLevelColor = (level) => {
    const colors = {
      DEBUG: '#6c757d',
      INFO: '#0dcaf0',
      WARNING: '#ffc107',
      ERROR: '#dc3545',
      CRITICAL: '#6f42c1',
    };
    return colors[level] || '#6c757d';
  };

  if (loading) {
    return <div className="loading">Loading logs...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Log Processing System</h1>
        <p>Distributed Systems Testing Framework - Day 6</p>
      </header>

      <main>
        <section className="log-form">
          <h2>Create New Log Event</h2>
          <form onSubmit={createLog}>
            <div className="form-group">
              <label htmlFor="message">Message:</label>
              <textarea
                id="message"
                value={newLog.message}
                onChange={(e) => setNewLog({ ...newLog, message: e.target.value })}
                placeholder="Enter log message..."
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="level">Level:</label>
              <select
                id="level"
                value={newLog.level}
                onChange={(e) => setNewLog({ ...newLog, level: e.target.value })}
              >
                <option value="DEBUG">Debug</option>
                <option value="INFO">Info</option>
                <option value="WARNING">Warning</option>
                <option value="ERROR">Error</option>
                <option value="CRITICAL">Critical</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="source">Source:</label>
              <input
                type="text"
                id="source"
                value={newLog.source}
                onChange={(e) => setNewLog({ ...newLog, source: e.target.value })}
                placeholder="Application name or source..."
              />
            </div>

            <button type="submit">Create Log</button>
          </form>
        </section>

        <section className="logs-list">
          <h2>Recent Log Events ({logs.length})</h2>
          {logs.length === 0 ? (
            <p>No logs available</p>
          ) : (
            <div className="logs">
              {logs.map((log) => (
                <div key={log.id} className="log-item">
                  <div className="log-header">
                    <span
                      className="log-level"
                      style={{ backgroundColor: getLevelColor(log.level) }}
                    >
                      {log.level}
                    </span>
                    <span className="log-timestamp">
                      {new Date(log.timestamp).toLocaleString()}
                    </span>
                    {log.source && (
                      <span className="log-source">({log.source})</span>
                    )}
                  </div>
                  <div className="log-message">{log.message}</div>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
