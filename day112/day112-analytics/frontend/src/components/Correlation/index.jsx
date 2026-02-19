import React, { useState, useEffect } from 'react'
import { fetchCorrelations } from '../../api/client'

const METRICS_LABELS = {
  page_views:    'Page Views',
  sessions:      'Sessions',
  revenue:       'Revenue',
  response_time: 'Resp. Time',
  error_rate:    'Error Rate',
}

function getColor(val) {
  const abs = Math.abs(val)
  if (abs < 0.2) return { bg: '#21262d', text: '#6e7681' }
  if (val > 0)   return { bg: `rgba(82,183,136,${0.15 + abs * 0.6})`, text: abs > 0.6 ? '#d8f3dc' : '#52b788' }
  return           { bg: `rgba(248,81,73,${0.15 + abs * 0.6})`,  text: abs > 0.6 ? '#ffd7d5' : '#f85149' }
}

export default function CorrelationPanel() {
  const [data, setData]     = useState(null)
  const [method, setMethod] = useState('pearson')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    fetchCorrelations(method).then(d => { setData(d); setLoading(false) })
  }, [method])

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, color: '#e2e8f0' }}>Correlation Analysis</h1>
        <p style={{ color: '#8b949e', fontSize: 13, marginTop: 4 }}>Pearson / Spearman correlation matrix across all metrics</p>
      </div>

      <div style={{ marginBottom: 20 }}>
        {['pearson','spearman'].map(m => (
          <button key={m} onClick={() => setMethod(m)} style={{
            marginRight: 8, padding: '8px 18px', borderRadius: 8, border: 'none', cursor: 'pointer', fontSize: 12, fontWeight: 600,
            background: method === m ? '#2d6a4f' : '#21262d',
            color: method === m ? '#d8f3dc' : '#8b949e',
          }}>{m.charAt(0).toUpperCase() + m.slice(1)}</button>
        ))}
      </div>

      {loading ? (
        <div style={{ color: '#8b949e' }}>Computing correlations...</div>
      ) : data?.matrix?.length > 0 && (
        <div style={{ background: '#161b22', border: '1px solid #21262d', borderRadius: 12, padding: '28px' }}>
          <h2 style={{ fontSize: 14, fontWeight: 600, color: '#e2e8f0', marginBottom: 24 }}>
            {method.charAt(0).toUpperCase() + method.slice(1)} Correlation Heatmap
          </h2>

          <div style={{ overflowX: 'auto' }}>
            <table style={{ borderCollapse: 'separate', borderSpacing: 4 }}>
              <thead>
                <tr>
                  <th style={{ width: 90 }} />
                  {data.metrics.map(m => (
                    <th key={m} style={{ width: 90, fontSize: 10, color: '#8b949e', fontWeight: 500, textAlign: 'center', paddingBottom: 8 }}>
                      {METRICS_LABELS[m] || m}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.matrix.map((row, i) => (
                  <tr key={i}>
                    <td style={{ fontSize: 10, color: '#8b949e', paddingRight: 8, textAlign: 'right', fontWeight: 500 }}>
                      {METRICS_LABELS[data.metrics[i]] || data.metrics[i]}
                    </td>
                    {row.map((val, j) => {
                      const c = getColor(val)
                      return (
                        <td key={j} title={`${data.metrics[i]} × ${data.metrics[j]}: ${val}`} style={{
                          width: 90, height: 72, textAlign: 'center', verticalAlign: 'middle',
                          background: c.bg, borderRadius: 8, cursor: 'default',
                          transition: 'transform 0.1s',
                        }}>
                          <div style={{ fontSize: 16, fontWeight: 700, color: c.text, fontFamily: 'JetBrains Mono' }}>
                            {val.toFixed(2)}
                          </div>
                        </td>
                      )
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div style={{ marginTop: 24, display: 'flex', gap: 20 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 11, color: '#8b949e' }}>
              <div style={{ width: 14, height: 14, borderRadius: 3, background: 'rgba(82,183,136,0.7)' }} /> Positive
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 11, color: '#8b949e' }}>
              <div style={{ width: 14, height: 14, borderRadius: 3, background: 'rgba(248,81,73,0.7)' }} /> Negative
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 11, color: '#8b949e' }}>
              <div style={{ width: 14, height: 14, borderRadius: 3, background: '#21262d' }} /> Weak / None
            </div>
          </div>

          {data.pairs?.filter(p => p.significant).length > 0 && (
            <div style={{ marginTop: 24 }}>
              <div style={{ fontSize: 13, fontWeight: 600, color: '#e2e8f0', marginBottom: 12 }}>Statistically Significant Pairs (p &lt; 0.05)</div>
              {data.pairs.filter(p => p.significant).map((p, i) => (
                <div key={i} style={{ display: 'flex', gap: 12, alignItems: 'center', marginBottom: 8, fontSize: 12 }}>
                  <span style={{ color: '#52b788', fontFamily: 'JetBrains Mono', fontWeight: 600 }}>
                    {METRICS_LABELS[p.x]} × {METRICS_LABELS[p.y]}
                  </span>
                  <span style={{ color: p.correlation > 0 ? '#52b788' : '#f85149', fontFamily: 'JetBrains Mono' }}>
                    r = {p.correlation.toFixed(4)}
                  </span>
                  <span style={{ color: '#6e7681' }}>p = {p.p_value.toFixed(4)}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
