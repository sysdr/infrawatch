import React, { useState } from 'react';
import axios from 'axios';

const API = 'http://localhost:8117';

export function TestControls({ onRunStarted }) {
  const [config, setConfig] = useState({
    name: 'Load Test Run',
    test_type: 'load',
    target_url: 'http://localhost:8117',
    users: 15,
    duration_seconds: 30,
    error_threshold_percent: 5,
  });
  const [loading, setLoading] = useState(false);
  const [lastRunId, setLastRunId] = useState(null);

  const startTest = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${API}/api/tests/start`, config);
      setLastRunId(res.data.run_id);
      onRunStarted(res.data.run_id, config.test_type);
    } catch (e) {
      alert('Failed to start test: ' + e.message);
    } finally {
      setLoading(false);
    }
  };

  const inp = (field, type = 'text') => ({
    value: config[field],
    onChange: (e) => setConfig(p => ({ ...p, [field]: type === 'number' ? Number(e.target.value) : e.target.value })),
    style: inputStyle,
  });

  return (
    <div style={cardStyle}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
        <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#4caf50' }} />
        <h3 style={{ margin: 0, color: '#e2e8f0', fontSize: '15px', fontWeight: '600' }}>Test Configuration</h3>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
        <div style={fieldStyle}>
          <label style={labelStyle}>Test Name</label>
          <input {...inp('name')} placeholder="My Load Test" />
        </div>
        <div style={fieldStyle}>
          <label style={labelStyle}>Test Type</label>
          <select value={config.test_type} onChange={e => setConfig(p => ({ ...p, test_type: e.target.value }))} style={inputStyle}>
            <option value="load">Load Test</option>
            <option value="benchmark">Benchmark</option>
            <option value="stress">Stress Test</option>
          </select>
        </div>
        <div style={{ ...fieldStyle, gridColumn: '1 / -1' }}>
          <label style={labelStyle}>Target URL</label>
          <input {...inp('target_url')} placeholder="http://localhost:8117" />
        </div>
        <div style={fieldStyle}>
          <label style={labelStyle}>Virtual Users</label>
          <input {...inp('users', 'number')} type="number" min={1} max={100} />
        </div>
        <div style={fieldStyle}>
          <label style={labelStyle}>Duration (seconds)</label>
          <input {...inp('duration_seconds', 'number')} type="number" min={5} max={300} />
        </div>
      </div>

      <button onClick={startTest} disabled={loading} style={btnStyle(loading)}>
        {loading ? '⟳ Starting...' : '▶ Start Test'}
      </button>

      {lastRunId && (
        <div style={{ marginTop: '12px', padding: '8px 12px', background: '#0f172a', borderRadius: '6px',
          fontSize: '11px', color: '#64748b', fontFamily: 'monospace' }}>
          Run ID: {lastRunId}
        </div>
      )}
    </div>
  );
}

const cardStyle = {
  background: '#1e293b', borderRadius: '12px', padding: '20px',
  border: '1px solid #334155',
};
const fieldStyle = { display: 'flex', flexDirection: 'column', gap: '6px' };
const labelStyle = { color: '#94a3b8', fontSize: '11px', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.05em' };
const inputStyle = {
  background: '#0f172a', border: '1px solid #334155', borderRadius: '6px',
  color: '#e2e8f0', padding: '8px 12px', fontSize: '13px', outline: 'none',
  width: '100%', boxSizing: 'border-box',
};
const btnStyle = (loading) => ({
  marginTop: '16px', width: '100%', padding: '12px',
  background: loading ? '#1e4620' : 'linear-gradient(135deg, #2e7d32, #4caf50)',
  border: 'none', borderRadius: '8px', color: '#fff',
  fontSize: '14px', fontWeight: '700', cursor: loading ? 'not-allowed' : 'pointer',
  letterSpacing: '0.05em',
});
