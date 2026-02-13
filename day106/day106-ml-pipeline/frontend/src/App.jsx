import React, { useState, useEffect, useCallback } from 'react'
import { api } from './services/api.js'

const NAV = [
  { id: 'anomaly', label: 'Anomaly Detection', icon: '⚡' },
  { id: 'forecast', label: 'Predictive Analytics', icon: '📈' },
  { id: 'patterns', label: 'Pattern Recognition', icon: '🔍' },
  { id: 'evaluation', label: 'Model Evaluation', icon: '📊' }
]

export default function App() {
  const [tab, setTab] = useState('anomaly')
  const [pipelineReady, setPipelineReady] = useState(false)
  const [training, setTraining] = useState(false)
  const [statusMsg, setStatusMsg] = useState('Checking...')
  const [lastTrained, setLastTrained] = useState(null)
  const [liveEvents, setLiveEvents] = useState([])

  const checkStatus = useCallback(async () => {
    try {
      const r = await api.status()
      setPipelineReady(r.data.is_ready)
      if (r.data.last_trained) setLastTrained(r.data.last_trained)
      setStatusMsg(r.data.is_ready ? 'Pipeline Ready' : 'Not Trained')
    } catch { setStatusMsg('Backend offline') }
  }, [])

  useEffect(() => { checkStatus() }, [checkStatus])

  // Re-check status periodically (e.g. after training via start.sh)
  useEffect(() => {
    const iv = setInterval(checkStatus, 10000)
    return () => clearInterval(iv)
  }, [checkStatus])

  useEffect(() => {
    if (!pipelineReady) return
    const poll = async () => {
      try {
        const r = await api.latestAnomaly()
        setLiveEvents(prev => [{ id: Date.now(), ...r.data }, ...prev.slice(0, 14)])
      } catch (e) {
        console.warn('Live anomaly fetch failed:', e?.message)
      }
    }
    poll()
    const interval = setInterval(poll, 5000)
    return () => clearInterval(interval)
  }, [pipelineReady])

  const handleTrain = async () => {
    setTraining(true)
    setStatusMsg('Training...')
    try {
      await api.train(500)
      await checkStatus()
      setStatusMsg('Pipeline Ready')
      setLiveEvents([]) // Clear so fresh data loads
    } catch (e) {
      setStatusMsg('Training failed')
      console.error('Train failed:', e?.message)
    }
    setTraining(false)
  }

  return (
    <div style={{ minHeight: '100vh', background: '#0f1117', display: 'flex', flexDirection: 'column' }}>
      <header style={{ background: '#141720', padding: '0 24px', height: 56, display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #1e2435' }}>
        <div style={{ fontWeight: 700, color: '#f1f5f9' }}>ML Pipeline — Day 106</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <span style={{ fontSize: 12, color: pipelineReady ? '#22c55e' : '#f59e0b' }}>{statusMsg}</span>
          <button onClick={handleTrain} disabled={training} style={{
            background: training ? '#374151' : '#22c55e', color: '#fff', border: 'none', borderRadius: 8,
            padding: '8px 20px', fontSize: 13, fontWeight: 600, cursor: training ? 'not-allowed' : 'pointer'
          }}>
            {training ? '⏳ Training...' : '🚀 Train Pipeline'}
          </button>
        </div>
      </header>

      {liveEvents.length > 0 && (
        <div style={{ background: '#111827', padding: '6px 24px', display: 'flex', gap: 16, overflowX: 'auto', flexWrap: 'wrap' }}>
          {liveEvents.slice(0, 5).map(a => (
            <span key={a.id} style={{
              fontSize: 11, padding: '2px 10px', borderRadius: 99,
              background: a.anomaly?.is_anomaly ? '#dc262620' : '#22c55e20',
              color: a.anomaly?.is_anomaly ? '#ef4444' : '#22c55e'
            }}>
              {a.anomaly?.is_anomaly ? '⚠' : '✓'} Score: {a.anomaly?.anomaly_score?.toFixed(3)}
            </span>
          ))}
        </div>
      )}

      <div style={{ display: 'flex', flex: 1 }}>
        <nav style={{ width: 200, background: '#141720', padding: 16, borderRight: '1px solid #1e2435' }}>
          {NAV.map(n => (
            <button key={n.id} onClick={() => setTab(n.id)} style={{
              width: '100%', padding: '10px 14px', marginBottom: 4, borderRadius: 8, border: 'none',
              background: tab === n.id ? '#22c55e18' : 'transparent', color: tab === n.id ? '#22c55e' : '#94a3b8',
              fontSize: 13, cursor: 'pointer', textAlign: 'left'
            }}>{n.icon} {n.label}</button>
          ))}
        </nav>

        <main style={{ flex: 1, padding: 24, overflow: 'auto' }}>
          {!pipelineReady && (
            <div style={{ textAlign: 'center', padding: 60, background: '#1e2435', borderRadius: 12, marginBottom: 24 }}>
              <div style={{ fontSize: 48, marginBottom: 16 }}>🤖</div>
              <div style={{ fontSize: 20, fontWeight: 700, color: '#f1f5f9', marginBottom: 8 }}>ML Pipeline Not Trained</div>
              <div style={{ fontSize: 14, color: '#64748b', marginBottom: 24 }}>Click "Train Pipeline" to train all models</div>
              <button onClick={handleTrain} disabled={training} style={{
                background: '#22c55e', color: '#fff', border: 'none', borderRadius: 10, padding: '12px 32px',
                fontSize: 15, fontWeight: 700, cursor: 'pointer'
              }}>{training ? '⏳ Training...' : '🚀 Train All Models'}</button>
            </div>
          )}

          {tab === 'anomaly' && pipelineReady && <AnomalyPanel />}
          {tab === 'forecast' && pipelineReady && <ForecastPanel />}
          {tab === 'patterns' && pipelineReady && <PatternPanel />}
          {tab === 'evaluation' && pipelineReady && <EvaluationPanel />}
        </main>
      </div>
    </div>
  )
}

function AnomalyPanel() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const load = () => {
    setError(null)
    api.batchAnomalies(80).then(r => {
      const d = r.data?.data || []
      if (d.length === 0) { setLoading(false); return }
      const anomalies = d.filter(x => x.is_anomaly)
      const scores = d.map(x => x.anomaly_score)
      setData({ total: d.length, anomalyCount: anomalies.length, anomalyRate: ((anomalies.length / d.length) * 100).toFixed(1), avgScore: (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(3) })
      setLoading(false)
    }).catch(e => { setLoading(false); setError(e?.message || 'Failed to load') })
  }
  useEffect(() => {
    load()
    const iv = setInterval(load, 10000)
    return () => clearInterval(iv)
  }, [])
  if (error) return <div style={{ color: '#ef4444', padding: 24 }}>Error: {error}. Ensure backend is running on port 8106.</div>
  if (loading || !data) return <div style={{ color: '#64748b' }}>Loading...</div>
  return (
    <div>
      <h2 style={{ fontSize: 20, marginBottom: 20, color: '#f1f5f9' }}>⚡ Anomaly Detection</h2>
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 24 }}>
        {[
          { label: 'Total Samples', value: data.total, color: '#60a5fa' },
          { label: 'Anomalies', value: data.anomalyCount, color: '#f97316' },
          { label: 'Anomaly Rate', value: data.anomalyRate + '%', color: '#f59e0b' },
          { label: 'Avg Score', value: data.avgScore, color: '#a78bfa' }
        ].map(c => (
          <div key={c.label} style={{ background: '#141720', border: '1px solid #1e2435', borderRadius: 10, padding: 16, minWidth: 140 }}>
            <div style={{ fontSize: 22, fontWeight: 700, color: c.color }}>{c.value}</div>
            <div style={{ fontSize: 12, color: '#64748b' }}>{c.label}</div>
          </div>
        ))}
      </div>
      <p style={{ color: '#64748b', fontSize: 13 }}>Isolation Forest scoring 80 infrastructure snapshots · Contamination: 5%</p>
    </div>
  )
}

function ForecastPanel() {
  const [forecasts, setForecasts] = useState({})
  const [metric, setMetric] = useState('cpu_usage')
  const [loading, setLoading] = useState(true)
  const load = () => api.allForecasts().then(r => { setForecasts(r.data); setLoading(false) }).catch(() => setLoading(false))
  useEffect(() => {
    load()
    const iv = setInterval(load, 15000)
    return () => clearInterval(iv)
  }, [])
  const current = forecasts[metric]
  const metrics = [{ key: 'cpu_usage', label: 'CPU' }, { key: 'memory_usage', label: 'Memory' }, { key: 'request_rate', label: 'Requests' }, { key: 'error_rate', label: 'Errors' }, { key: 'latency_p99', label: 'Latency' }]
  if (loading) return <div style={{ color: '#64748b' }}>Loading...</div>
  return (
    <div>
      <h2 style={{ fontSize: 20, marginBottom: 20, color: '#f1f5f9' }}>📈 Predictive Analytics</h2>
      <div style={{ display: 'flex', gap: 8, marginBottom: 20, flexWrap: 'wrap' }}>
        {metrics.map(m => (
          <button key={m.key} onClick={() => setMetric(m.key)} style={{
            padding: '7px 16px', borderRadius: 8, fontSize: 12, border: `1px solid ${metric === m.key ? '#22c55e' : '#1e2435'}`,
            background: metric === m.key ? '#22c55e22' : 'transparent', color: metric === m.key ? '#22c55e' : '#64748b', cursor: 'pointer'
          }}>{m.label}</button>
        ))}
      </div>
      {current && (
        <div>
          <div style={{ display: 'flex', gap: 12, marginBottom: 20, flexWrap: 'wrap' }}>
            <div style={{ background: '#141720', padding: 16, borderRadius: 10, minWidth: 150 }}>
              <div style={{ fontSize: 20, fontWeight: 700, color: '#22c55e' }}>{Math.max(...current.forecast).toFixed(1)}</div>
              <div style={{ fontSize: 12, color: '#64748b' }}>Peak Forecast</div>
            </div>
            <div style={{ background: '#141720', padding: 16, borderRadius: 10, minWidth: 150 }}>
              <div style={{ fontSize: 20, fontWeight: 700, color: '#60a5fa' }}>{Math.min(...current.forecast).toFixed(1)}</div>
              <div style={{ fontSize: 12, color: '#64748b' }}>Min Forecast</div>
            </div>
            <div style={{ background: '#141720', padding: 16, borderRadius: 10, minWidth: 150 }}>
              <div style={{ fontSize: 20, fontWeight: 700, color: '#a78bfa' }}>{(current.forecast.reduce((a, b) => a + b, 0) / current.forecast.length).toFixed(1)}</div>
              <div style={{ fontSize: 12, color: '#64748b' }}>Avg Forecast</div>
            </div>
          </div>
          <p style={{ color: '#64748b', fontSize: 13 }}>ARIMA 24-hour forecasting · {current.timestamps?.length || 0} steps</p>
        </div>
      )}
    </div>
  )
}

function PatternPanel() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  useEffect(() => {
    api.patterns().then(r => { setData(r.data); setLoading(false) }).catch(() => setLoading(false))
  }, [])
  if (loading || !data) return <div style={{ color: '#64748b' }}>Loading...</div>
  const profiles = data.cluster_profiles || {}
  return (
    <div>
      <h2 style={{ fontSize: 20, marginBottom: 20, color: '#f1f5f9' }}>🔍 Pattern Recognition</h2>
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 24 }}>
        {Object.entries(profiles).map(([id, p]) => (
          <div key={id} style={{ background: '#141720', border: '1px solid #1e2435', borderRadius: 12, padding: 16, minWidth: 180 }}>
            <div style={{ fontSize: 14, fontWeight: 700, color: '#22c55e', marginBottom: 4 }}>{p.label}</div>
            <div style={{ fontSize: 12, color: '#64748b' }}>{p.count} samples</div>
            <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 4 }}>CPU: {p.profile?.cpu_usage?.toFixed(0)}% · Mem: {p.profile?.memory_usage?.toFixed(0)}%</div>
          </div>
        ))}
      </div>
      <p style={{ color: '#64748b', fontSize: 13 }}>KMeans · {data.n_clusters || 3} clusters · Silhouette: {data.silhouette_score?.toFixed(3) || '—'}</p>
    </div>
  )
}

function EvaluationPanel() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const load = () => api.evaluation().then(r => { setData(r.data); setLoading(false) }).catch(() => setLoading(false))
  useEffect(() => {
    load()
    const i = setInterval(() => api.evaluation().then(r => setData(r.data)).catch(() => {}), 10000)
    return () => clearInterval(i)
  }, [])
  if (loading || !data) return <div style={{ color: '#64748b' }}>Loading...</div>
  const ad = data.anomaly_model || {}
  const fc = data.forecast_model || {}
  const pt = data.pattern_model || {}
  return (
    <div>
      <h2 style={{ fontSize: 20, marginBottom: 20, color: '#f1f5f9' }}>📊 Model Evaluation</h2>
      <div style={{ padding: 14, borderRadius: 10, marginBottom: 24, background: data.overall_health ? '#22c55e15' : '#ef444415', border: `1px solid ${data.overall_health ? '#22c55e40' : '#ef444440'}` }}>
        <span style={{ fontSize: 24 }}>{data.overall_health ? '✅' : '⚠️'}</span>
        <span style={{ marginLeft: 12, fontWeight: 700, color: data.overall_health ? '#22c55e' : '#ef4444' }}>
          {data.overall_health ? 'All Models Healthy' : 'Model Health Warning'}
        </span>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 16 }}>
        {[
          { label: 'Anomaly Rate', value: (ad.anomaly_rate ?? 0).toFixed(4), status: ad.is_healthy },
          { label: 'Forecast RMSE', value: (fc.avg_rmse ?? 0).toFixed(4), status: fc.is_healthy },
          { label: 'Silhouette', value: (pt.silhouette_score ?? 0).toFixed(4), status: pt.is_healthy },
          { label: 'Drift Score', value: (ad.drift_score ?? 0).toFixed(4), status: (ad.drift_score ?? 0) < 0.3 }
        ].map(c => (
          <div key={c.label} style={{ background: '#141720', border: '1px solid #1e2435', borderRadius: 12, padding: 16 }}>
            <div style={{ fontSize: 18, fontWeight: 700, color: '#f1f5f9', fontFamily: 'monospace' }}>{c.value}</div>
            <div style={{ fontSize: 12, color: '#64748b' }}>{c.label}</div>
            <div style={{ fontSize: 10, marginTop: 4, color: c.status ? '#22c55e' : '#ef4444' }}>{c.status ? '● Healthy' : '● Degraded'}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
