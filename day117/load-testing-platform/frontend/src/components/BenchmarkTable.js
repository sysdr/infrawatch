import React from 'react';

export function BenchmarkTable({ benchmarks }) {
  if (!benchmarks || !benchmarks.length) return (
    <div style={emptyStyle}>No benchmark data yet. Start a Benchmark test.</div>
  );

  const cols = ['Endpoint', 'Method', 'p50 ms', 'p95 ms', 'p99 ms', 'Mean ms', 'RPS', 'Errors'];

  return (
    <div style={{ background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', overflow: 'hidden' }}>
      <div style={{ padding: '16px 20px', borderBottom: '1px solid #334155' }}>
        <span style={hdrStyle}>Endpoint Benchmark Report</span>
      </div>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#0f172a' }}>
              {cols.map(c => (
                <th key={c} style={thStyle}>{c}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {benchmarks.map((b, i) => (
              <tr key={i} style={{ borderBottom: '1px solid #1e3a5f' }}>
                <td style={{ ...tdStyle, color: '#4caf50', fontFamily: 'monospace', fontSize: '12px' }}>{b.endpoint}</td>
                <td style={{ ...tdStyle, color: '#2196f3' }}>{b.method}</td>
                <td style={metricTd(b.p50_ms, 100)}>{b.p50_ms}</td>
                <td style={metricTd(b.p95_ms, 200)}>{b.p95_ms}</td>
                <td style={metricTd(b.p99_ms, 500)}>{b.p99_ms}</td>
                <td style={tdStyle}>{b.mean_ms}</td>
                <td style={{ ...tdStyle, color: '#4caf50' }}>{b.throughput_rps}</td>
                <td style={{ ...tdStyle, color: b.error_count > 0 ? '#f44336' : '#64748b' }}>{b.error_count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const hdrStyle = { color: '#94a3b8', fontSize: '11px', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.05em' };
const thStyle = { color: '#64748b', fontSize: '10px', fontWeight: '600', padding: '8px 16px',
  textAlign: 'left', textTransform: 'uppercase', letterSpacing: '0.05em' };
const tdStyle = { color: '#e2e8f0', fontSize: '13px', padding: '10px 16px' };
const emptyStyle = { padding: '24px', color: '#64748b', textAlign: 'center', fontStyle: 'italic', fontSize: '13px' };
const metricTd = (val, threshold) => ({
  ...tdStyle, color: val < threshold * 0.5 ? '#4caf50' : val < threshold ? '#ff9800' : '#f44336',
  fontWeight: '600',
});
