import React, { useState, useEffect } from 'react';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [health, setHealth] = useState(null);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE}/health`)
      .then(r => r.json())
      .then(data => setHealth(data))
      .catch(() => setHealth({ status: 'error' }));
  }, []);

  useEffect(() => {
    fetch(`${API_BASE}/api/logs/search?q=*&limit=20`)
      .then(r => r.json())
      .then(data => setLogs(data.logs || data.items || []))
      .catch(() => setLogs([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div style={{ padding: '2rem', maxWidth: 1200, margin: '0 auto' }}>
      <h1>Log Management UI</h1>
      <p style={{ color: health?.status === 'ok' ? '#22c55e' : '#ef4444' }}>
        {health?.status === 'ok' ? '✓ Backend connected' : '✗ Backend unavailable'}
      </p>
      <section>
        <h2>Recent Logs</h2>
        {loading ? <p>Loading...</p> : logs.length === 0 ? (
          <p style={{ color: '#64748b' }}>No logs found. Run generate_logs.py to populate.</p>
        ) : (
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {logs.slice(0, 10).map((log, i) => (
              <li key={i} style={{ padding: '0.75rem', marginBottom: '0.5rem', background: '#1e293b', borderRadius: 8, fontFamily: 'monospace' }}>
                {log.message || log.content || JSON.stringify(log)}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

export default App;
