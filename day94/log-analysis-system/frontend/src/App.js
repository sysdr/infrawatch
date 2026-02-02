import React, { useState, useEffect } from 'react';
import './App.css';
import { getApiBase, api } from './api';
import PatternDashboard from './components/PatternDashboard';
import AnomalyDashboard from './components/AnomalyDashboard';
import TrendDashboard from './components/TrendDashboard';
import AlertDashboard from './components/AlertDashboard';
import LogSimulator from './components/LogSimulator';

class AppErrorBoundary extends React.Component {
  state = { hasError: false, error: null };
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '2rem', fontFamily: 'sans-serif', maxWidth: '600px' }}>
          <h2>Something went wrong</h2>
          <pre style={{ background: '#f5f5f5', padding: '1rem', overflow: 'auto' }}>
            {this.state.error?.message || 'Unknown error'}
          </pre>
        </div>
      );
    }
    return this.props.children;
  }
}

function App() {
  const [activeTab, setActiveTab] = useState('patterns');
  const [ws, setWs] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [showDemoData, setShowDemoData] = useState(true);
  const [loadDemoStatus, setLoadDemoStatus] = useState(null);
  const [backendStatus, setBackendStatus] = useState('checking'); // 'checking' | 'connected' | 'offline'

  // On mount: check backend and auto-load demo data so real data shows immediately
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const health = await api.get('/api/health');
        if (cancelled) return;
        setBackendStatus('connected');
        // Auto-seed demo data so dashboard shows real data
        const seed = await api.post('/api/demo/seed');
        if (cancelled) return;
        setShowDemoData(false);
        setLoadDemoStatus('done');
        setRefreshTrigger(t => t + 1);
      } catch (e) {
        if (!cancelled) {
          setBackendStatus('offline');
        }
      }
    })();
    return () => { cancelled = true; };
  }, []);

  // WebSocket for real-time updates — always use same-origin so dev proxy forwards /ws to backend
  useEffect(() => {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.host}/ws`;
    let websocket = null;
    let mounted = true;
    let tid = 0;
    const connect = () => {
      if (!mounted) return;
      try {
        websocket = new WebSocket(wsUrl);
        websocket.onopen = () => { if (mounted) setWs(websocket); };
        websocket.onclose = () => { if (mounted) setWs(null); };
        websocket.onerror = () => { /* silenced — proxy/backend may be down */ };
      } catch (_) {}
    };
    // Delay to avoid React Strict Mode double-mount closing ws before it connects
    tid = window.setTimeout(connect, 500);
    return () => {
      mounted = false;
      window.clearTimeout(tid);
      if (websocket) {
        websocket.onopen = websocket.onclose = websocket.onerror = null;
        websocket.close();
      }
    };
  }, []);

  const handleLoadDemo = async () => {
    setLoadDemoStatus('loading');
    try {
      await api.post('/api/demo/seed');
      setBackendStatus('connected');
      setShowDemoData(false);
      setRefreshTrigger(t => t + 1);
      setActiveTab('patterns');
      setLoadDemoStatus('done');
    } catch (err) {
      setBackendStatus('offline');
    }
  };

  return (
    <AppErrorBoundary>
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <h1>🔍 Log Analysis System</h1>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
            <div className="status-badge" style={{
              padding: '0.35rem 0.75rem',
              borderRadius: '20px',
              fontSize: '0.85rem',
              fontWeight: 600,
              background: backendStatus === 'connected' ? 'rgba(34,197,94,0.3)' : backendStatus === 'offline' ? 'rgba(239,68,68,0.3)' : 'rgba(255,255,255,0.2)',
              border: '1px solid ' + (backendStatus === 'connected' ? 'rgba(34,197,94,0.6)' : backendStatus === 'offline' ? 'rgba(239,68,68,0.6)' : 'rgba(255,255,255,0.5)'),
            }}>
              {backendStatus === 'connected' && '● Running — Well Done!'}
              {backendStatus === 'offline' && '○ Backend Offline'}
              {backendStatus === 'checking' && '○ Connecting...'}
            </div>
            <button
              className="demo-button"
              onClick={handleLoadDemo}
              disabled={loadDemoStatus === 'loading'}
              style={{
                padding: '0.5rem 1rem',
                borderRadius: '8px',
                border: '1px solid rgba(255,255,255,0.6)',
                background: 'rgba(255,255,255,0.15)',
                color: 'white',
                cursor: loadDemoStatus === 'loading' ? 'wait' : 'pointer',
                fontWeight: 600,
                fontSize: '0.9rem',
              }}
            >
              {loadDemoStatus === 'loading' ? '⏳ Loading...' : '📊 Load Demo Data'}
            </button>
          </div>
        </div>
      </header>

      {showDemoData && backendStatus === 'offline' && (
        <div style={{ background: 'linear-gradient(90deg, #dbeafe 0%, #e0e7ff 100%)', padding: '0.75rem 2rem', borderBottom: '1px solid #bfdbfe', fontSize: '0.95rem' }}>
          <strong>Welcome!</strong> You are viewing sample data. Click <strong>Load Demo Data</strong> above to populate with real data from the backend, then explore Patterns, Anomalies, Trends, and Alerts. Or use the <strong>Simulator</strong> tab to generate your own logs.
        </div>
      )}

      <nav className="tab-navigation">
        <button 
          className={activeTab === 'patterns' ? 'active' : ''}
          onClick={() => setActiveTab('patterns')}
        >
          📊 Patterns
        </button>
        <button 
          className={activeTab === 'anomalies' ? 'active' : ''}
          onClick={() => setActiveTab('anomalies')}
        >
          ⚠️ Anomalies
        </button>
        <button 
          className={activeTab === 'trends' ? 'active' : ''}
          onClick={() => setActiveTab('trends')}
        >
          📈 Trends
        </button>
        <button 
          className={activeTab === 'alerts' ? 'active' : ''}
          onClick={() => setActiveTab('alerts')}
        >
          🔔 Alerts
        </button>
        <button 
          className={activeTab === 'simulator' ? 'active' : ''}
          onClick={() => setActiveTab('simulator')}
        >
          🎮 Simulator
        </button>
      </nav>

      <main className="app-content">
        {activeTab === 'patterns' && <PatternDashboard key={refreshTrigger} ws={ws} refreshTrigger={refreshTrigger} showDemoData={showDemoData} />}
        {activeTab === 'anomalies' && <AnomalyDashboard key={refreshTrigger} ws={ws} refreshTrigger={refreshTrigger} showDemoData={showDemoData} />}
        {activeTab === 'trends' && <TrendDashboard key={refreshTrigger} ws={ws} refreshTrigger={refreshTrigger} showDemoData={showDemoData} />}
        {activeTab === 'alerts' && <AlertDashboard key={refreshTrigger} ws={ws} refreshTrigger={refreshTrigger} showDemoData={showDemoData} />}
        {activeTab === 'simulator' && (
          <LogSimulator
            onSimulationStart={() => setShowDemoData(false)}
            onComplete={() => {
              setRefreshTrigger(t => t + 1);
              setActiveTab('patterns'); // Auto-switch to see results
            }}
          />
        )}
      </main>

      <footer className="app-footer">
        <p>
          {backendStatus === 'connected' ? (
            <>✅ Well Done — Dashboard Running | Day 94: Log Analysis System</>
          ) : (
            <>Day 94: Log Analysis System | Built with React + FastAPI</>
          )}
        </p>
      </footer>
    </div>
    </AppErrorBoundary>
  );
}

export default App;
