import React, { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { fetchReport } from '../../api/client'

export default function ReportsPanel() {
  const [days, setDays]     = useState(7)
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    fetchReport(days).then(d => { setReport(d); setLoading(false) })
  }, [days])

  const daily = []
  if (report?.hourly) {
    const grouped = {}
    report.hourly.forEach(h => {
      const day = h.timestamp.split('T')[0]
      if (!grouped[day]) grouped[day] = { page_views: 0, sessions: 0, revenue: 0 }
      grouped[day].page_views += h.page_views
      grouped[day].sessions   += h.sessions
      grouped[day].revenue    += h.revenue
    })
    Object.entries(grouped).forEach(([day, vals]) => {
      daily.push({ day: day.slice(5), ...vals, revenue: Math.round(vals.revenue) })
    })
  }

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, color: '#e2e8f0' }}>Advanced Reports</h1>
        <p style={{ color: '#8b949e', fontSize: 13, marginTop: 4 }}>Aggregated analytics with time-window filtering</p>
      </div>

      <div style={{ marginBottom: 20 }}>
        {[3, 7, 14, 30].map(d => (
          <button key={d} onClick={() => setDays(d)} style={{
            marginRight: 8, padding: '8px 18px', borderRadius: 8, border: 'none', cursor: 'pointer', fontSize: 12, fontWeight: 600,
            background: days === d ? '#2d6a4f' : '#21262d',
            color: days === d ? '#d8f3dc' : '#8b949e',
          }}>Last {d}d</button>
        ))}
      </div>

      {!loading && report?.summary && (
        <div style={{ display: 'flex', gap: 16, marginBottom: 24 }}>
          {[
            { label: 'Total Page Views', value: report.summary.total_page_views?.toLocaleString() },
            { label: 'Total Sessions',   value: report.summary.total_sessions?.toLocaleString() },
            { label: 'Total Revenue',    value: `$${report.summary.total_revenue?.toLocaleString()}` },
            { label: 'Avg Response Time', value: `${report.summary.avg_response_time}ms` },
          ].map(k => (
            <div key={k.label} style={{ background: '#161b22', border: '1px solid #21262d', borderRadius: 12, padding: '16px 20px', flex: 1 }}>
              <div style={{ fontSize: 10, color: '#8b949e', letterSpacing: '0.8px' }}>{k.label.toUpperCase()}</div>
              <div style={{ fontSize: 22, fontWeight: 700, color: '#52b788', fontFamily: 'JetBrains Mono', marginTop: 6 }}>{k.value}</div>
            </div>
          ))}
        </div>
      )}

      {daily.length > 0 && (
        <div style={{ background: '#161b22', border: '1px solid #21262d', borderRadius: 12, padding: '24px', marginBottom: 20 }}>
          <h2 style={{ fontSize: 14, fontWeight: 600, color: '#e2e8f0', marginBottom: 20 }}>Daily Page Views</h2>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={daily}>
              <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
              <XAxis dataKey="day" tick={{ fill: '#6e7681', fontSize: 10 }} />
              <YAxis tick={{ fill: '#6e7681', fontSize: 10 }} />
              <Tooltip contentStyle={{ background: '#1e2028', border: '1px solid #30363d', borderRadius: 8, color: '#e2e8f0', fontSize: 12 }} />
              <Bar dataKey="page_views" fill="#52b788" radius={[4, 4, 0, 0]} name="Page Views" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {daily.length > 0 && (
        <div style={{ background: '#161b22', border: '1px solid #21262d', borderRadius: 12, padding: '24px' }}>
          <h2 style={{ fontSize: 14, fontWeight: 600, color: '#e2e8f0', marginBottom: 16 }}>Daily Summary Table</h2>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
            <thead>
              <tr>
                {['Date', 'Page Views', 'Sessions', 'Revenue'].map(h => (
                  <th key={h} style={{ padding: '8px 16px', textAlign: 'left', color: '#6e7681', fontSize: 11, letterSpacing: '0.6px', borderBottom: '1px solid #21262d' }}>
                    {h.toUpperCase()}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {daily.map((row, i) => (
                <tr key={i} style={{ borderBottom: '1px solid #161b22' }}>
                  <td style={{ padding: '10px 16px', color: '#e2e8f0', fontFamily: 'JetBrains Mono', fontSize: 12 }}>{row.day}</td>
                  <td style={{ padding: '10px 16px', color: '#52b788', fontFamily: 'JetBrains Mono' }}>{row.page_views.toLocaleString()}</td>
                  <td style={{ padding: '10px 16px', color: '#f0883e', fontFamily: 'JetBrains Mono' }}>{row.sessions.toLocaleString()}</td>
                  <td style={{ padding: '10px 16px', color: '#ffa657', fontFamily: 'JetBrains Mono' }}>${row.revenue.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
