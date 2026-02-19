import React, { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { fetchKPIs, fetchReport } from '../../api/client'

const KPICard = ({ label, value, change, unit = '' }) => {
  const up = change >= 0
  return (
    <div style={{
      background: '#161b22', border: '1px solid #21262d', borderRadius: 12,
      padding: '20px 24px', flex: 1,
    }}>
      <div style={{ fontSize: 11, color: '#8b949e', letterSpacing: '0.8px', marginBottom: 8 }}>{label.toUpperCase()}</div>
      <div style={{ fontSize: 28, fontWeight: 700, color: '#e2e8f0', fontFamily: 'JetBrains Mono' }}>
        {unit}{typeof value === 'number' ? value.toLocaleString() : value}
      </div>
      <div style={{ fontSize: 12, marginTop: 6, color: up ? '#52b788' : '#f85149' }}>
        {up ? '▲' : '▼'} {Math.abs(change)}% vs last week
      </div>
    </div>
  )
}

export default function Dashboard() {
  const [kpis, setKpis]     = useState(null)
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([fetchKPIs(), fetchReport(7)]).then(([k, r]) => {
      setKpis(k); setReport(r); setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  if (loading) return <div style={{ color: '#8b949e', padding: 40 }}>Loading dashboard...</div>

  const chartData = (report?.hourly || []).slice(-48).map(h => ({
    time: new Date(h.timestamp).toLocaleTimeString('en', { hour: '2-digit', minute: '2-digit' }),
    pageViews: h.page_views,
    sessions: h.sessions,
    revenue: h.revenue,
  }))

  return (
    <div>
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, color: '#e2e8f0' }}>Analytics Overview</h1>
        <p style={{ color: '#8b949e', fontSize: 13, marginTop: 4 }}>Last 7 days · Auto-refreshed</p>
      </div>

      {kpis && (
        <div style={{ display: 'flex', gap: 16, marginBottom: 28 }}>
          <KPICard label="Page Views"    value={kpis.page_views?.value}    change={kpis.page_views?.change_pct} />
          <KPICard label="Sessions"      value={kpis.sessions?.value}      change={kpis.sessions?.change_pct} />
          <KPICard label="Revenue"       value={kpis.revenue?.value}       change={kpis.revenue?.change_pct}       unit="$" />
          <KPICard label="Resp Time (ms)" value={kpis.response_time?.value} change={kpis.response_time?.change_pct} />
        </div>
      )}

      <div style={{ background: '#161b22', border: '1px solid #21262d', borderRadius: 12, padding: '24px' }}>
        <h2 style={{ fontSize: 14, fontWeight: 600, color: '#e2e8f0', marginBottom: 20 }}>Page Views & Sessions — Last 48h</h2>
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
            <XAxis dataKey="time" tick={{ fill: '#6e7681', fontSize: 10 }} interval={5} />
            <YAxis tick={{ fill: '#6e7681', fontSize: 10 }} />
            <Tooltip contentStyle={{ background: '#1e2028', border: '1px solid #30363d', borderRadius: 8, color: '#e2e8f0', fontSize: 12 }} />
            <Line type="monotone" dataKey="pageViews" stroke="#52b788" strokeWidth={2} dot={false} name="Page Views" />
            <Line type="monotone" dataKey="sessions"  stroke="#f0883e" strokeWidth={1.5} dot={false} name="Sessions" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
