import React, { useState, useEffect } from 'react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend, LineChart, Line
} from 'recharts';

export function LiveCharts({ messages }) {
  const [throughputData, setThroughputData] = useState([]);
  const [latencyData, setLatencyData] = useState([]);

  useEffect(() => {
    const metricMsgs = messages.filter(m => m.type === 'metric' && m.rps !== undefined);
    if (!metricMsgs.length) return;

    const throughput = metricMsgs.slice(-60).map((m, i) => ({
      t: `${Math.round(m.elapsed_seconds || i * 2)}s`,
      rps: Math.round(m.rps || 0),
      users: m.active_users || 0,
    }));
    const latency = metricMsgs.slice(-60).map((m, i) => ({
      t: `${Math.round(m.elapsed_seconds || i * 2)}s`,
      p50: Math.round(m.p50_ms || 0),
      p95: Math.round(m.p95_ms || 0),
      p99: Math.round(m.p99_ms || 0),
    }));

    setThroughputData(throughput);
    setLatencyData(latency);
  }, [messages]);

  const chartStyle = {
    background: '#1e293b', borderRadius: '12px', padding: '16px',
    border: '1px solid #334155',
  };
  const titleStyle = { color: '#94a3b8', fontSize: '11px', fontWeight: '600',
    textTransform: 'uppercase', marginBottom: '12px', letterSpacing: '0.05em' };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
      <div style={chartStyle}>
        <div style={titleStyle}>Throughput (RPS) & Active Users</div>
        <ResponsiveContainer width="100%" height={180}>
          <AreaChart data={throughputData} isAnimationActive={false}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e3a5f" />
            <XAxis dataKey="t" tick={{ fill: '#64748b', fontSize: 10 }} />
            <YAxis tick={{ fill: '#64748b', fontSize: 10 }} />
            <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '6px' }}
              labelStyle={{ color: '#94a3b8' }} itemStyle={{ color: '#4caf50' }} />
            <Legend wrapperStyle={{ fontSize: '11px' }} />
            <Area type="monotone" dataKey="rps" stroke="#4caf50" fill="#1a3a1f" name="RPS" strokeWidth={2} />
            <Area type="monotone" dataKey="users" stroke="#2196f3" fill="#0d1f3c" name="Users" strokeWidth={1.5} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div style={chartStyle}>
        <div style={titleStyle}>Latency Percentiles (ms)</div>
        <ResponsiveContainer width="100%" height={180}>
          <LineChart data={latencyData} isAnimationActive={false}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e3a5f" />
            <XAxis dataKey="t" tick={{ fill: '#64748b', fontSize: 10 }} />
            <YAxis tick={{ fill: '#64748b', fontSize: 10 }} />
            <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '6px' }}
              labelStyle={{ color: '#94a3b8' }} />
            <Legend wrapperStyle={{ fontSize: '11px' }} />
            <Line type="monotone" dataKey="p50" stroke="#4caf50" name="p50" dot={false} strokeWidth={2} />
            <Line type="monotone" dataKey="p95" stroke="#ff9800" name="p95" dot={false} strokeWidth={2} />
            <Line type="monotone" dataKey="p99" stroke="#f44336" name="p99" dot={false} strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
