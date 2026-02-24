import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API = 'http://localhost:8117';

export function RunHistory({ refreshKey }) {
  const [runs, setRuns] = useState([]);

  useEffect(() => {
    axios.get(`${API}/api/tests/runs`).then(r => setRuns(r.data.runs || []));
  }, [refreshKey]);

  const statusColor = (s) => ({ completed: '#4caf50', running: '#2196f3', error: '#f44336' }[s] || '#94a3b8');

  return (
    <div style={{ background: '#1e293b', borderRadius: '12px', border: '1px solid #334155' }}>
      <div style={{ padding: '14px 20px', borderBottom: '1px solid #334155',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={hdrStyle}>Test Run History</span>
        <span style={{ color: '#64748b', fontSize: '11px' }}>{runs.length} runs</span>
      </div>
      {runs.length === 0 ? (
        <div style={{ padding: '20px', color: '#64748b', fontSize: '13px', textAlign: 'center' }}>
          No test runs yet.
        </div>
      ) : (
        <div style={{ maxHeight: '240px', overflowY: 'auto' }}>
          {runs.slice(0, 20).map(r => (
            <div key={r.id} style={{ padding: '12px 20px', borderBottom: '1px solid #0f172a',
              display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ color: '#e2e8f0', fontSize: '13px', fontWeight: '500' }}>{r.name}</div>
                <div style={{ color: '#64748b', fontSize: '11px', marginTop: '2px' }}>
                  {r.test_type} · {r.id.slice(0, 8)}
                </div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ color: statusColor(r.status), fontSize: '11px', fontWeight: '600',
                  textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  ● {r.status}
                </div>
                {r.summary?.p99_ms && (
                  <div style={{ color: '#64748b', fontSize: '11px', marginTop: '2px' }}>
                    p99: {r.summary.p99_ms}ms
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

const hdrStyle = { color: '#94a3b8', fontSize: '11px', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.05em' };
