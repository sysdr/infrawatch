import React, { useState, useEffect, useCallback } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine, Scatter, ScatterChart } from 'recharts'
import { fetchMLStatus, triggerTrain, fetchPredictions, fetchAnomalies } from '../../api/client'

const StateIndicator = ({ status }) => {
  const map = {
    idle:     { color: '#8b949e', label: 'IDLE' },
    training: { color: '#f0883e', label: 'TRAINING' },
    serving:  { color: '#52b788', label: 'SERVING' },
    error:    { color: '#f85149', label: 'ERROR' },
    degraded: { color: '#ffa657', label: 'DEGRADED' },
  }
  const s = map[status] || map.idle
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
      <div style={{
        width: 12, height: 12, borderRadius: '50%', background: s.color,
        boxShadow: `0 0 8px ${s.color}`,
        animation: status === 'training' ? 'pulse 1.2s infinite' : 'none'
      }} />
      <span style={{ fontSize: 13, fontWeight: 700, color: s.color }}>{s.label}</span>
    </div>
  )
}

export default function MLPanel() {
  const [mlStatus, setMlStatus]   = useState(null)
  const [preds, setPreds]         = useState([])
  const [anomalies, setAnomalies] = useState(null)
  const [training, setTraining]   = useState(false)
  const [hours, setHours]         = useState(24)

  const refresh = useCallback(() => {
    fetchMLStatus().then(setMlStatus)
    fetchPredictions(hours).then(d => setPreds(d.predictions || []))
    fetchAnomalies().then(setAnomalies)
  }, [hours])

  useEffect(() => { refresh(); const t = setInterval(refresh, 5000); return () => clearInterval(t) }, [refresh])

  const handleTrain = async () => {
    setTraining(true)
    await triggerTrain()
    setTimeout(() => { refresh(); setTraining(false) }, 3000)
  }

  const predChartData = preds.map((p, i) => ({
    hour:   i + 1,
    pred:   p.predicted,
    upper:  p.upper,
    lower:  p.lower,
  }))

  const anomalyData = (anomalies?.data || []).slice(-96).map((d, i) => ({
    x: i,
    y: d.page_views,
    anomaly: d.is_anomaly,
  }))

  return (
    <div>
      <style>{`@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.4}}`}</style>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, color: '#e2e8f0' }}>ML Model Engine</h1>
        <p style={{ color: '#8b949e', fontSize: 13, marginTop: 4 }}>RandomForest Trend Prediction · IsolationForest Anomaly Detection</p>
      </div>

      <div style={{ display: 'flex', gap: 16, marginBottom: 20 }}>
        <div style={{ background: '#161b22', border: '1px solid #21262d', borderRadius: 12, padding: '20px 24px', flex: 1 }}>
          <div style={{ fontSize: 11, color: '#8b949e', letterSpacing: '0.8px', marginBottom: 12 }}>MODEL STATE</div>
          <StateIndicator status={mlStatus?.status} />
          {mlStatus?.finished_at && (
            <div style={{ marginTop: 8, fontSize: 11, color: '#6e7681' }}>
              Trained at {new Date(mlStatus.finished_at).toLocaleTimeString()}
            </div>
          )}
        </div>
        {mlStatus?.metrics && (
          <>
            <div style={{ background: '#161b22', border: '1px solid #21262d', borderRadius: 12, padding: '20px 24px', flex: 1 }}>
              <div style={{ fontSize: 11, color: '#8b949e', marginBottom: 8 }}>R² SCORE</div>
              <div style={{ fontSize: 28, fontWeight: 700, color: '#52b788', fontFamily: 'JetBrains Mono' }}>
                {mlStatus.metrics.r2?.toFixed(4)}
              </div>
            </div>
            <div style={{ background: '#161b22', border: '1px solid #21262d', borderRadius: 12, padding: '20px 24px', flex: 1 }}>
              <div style={{ fontSize: 11, color: '#8b949e', marginBottom: 8 }}>MAE</div>
              <div style={{ fontSize: 28, fontWeight: 700, color: '#f0883e', fontFamily: 'JetBrains Mono' }}>
                {mlStatus.metrics.mae?.toFixed(1)}
              </div>
            </div>
            <div style={{ background: '#161b22', border: '1px solid #21262d', borderRadius: 12, padding: '20px 24px', flex: 1 }}>
              <div style={{ fontSize: 11, color: '#8b949e', marginBottom: 8 }}>ANOMALIES</div>
              <div style={{ fontSize: 28, fontWeight: 700, color: '#ffa657', fontFamily: 'JetBrains Mono' }}>
                {anomalies?.anomalies_found ?? '—'}
              </div>
            </div>
          </>
        )}
      </div>

      <div style={{ display: 'flex', gap: 12, marginBottom: 20 }}>
        <button onClick={handleTrain} disabled={training} style={{
          padding: '10px 22px', background: '#2d6a4f', color: '#d8f3dc',
          border: 'none', borderRadius: 8, cursor: 'pointer', fontSize: 13, fontWeight: 600,
        }}>
          {training ? '⟳ Training...' : '▶ Train Models'}
        </button>
        <select value={hours} onChange={e => setHours(Number(e.target.value))} style={{
          padding: '10px 16px', background: '#21262d', color: '#e2e8f0',
          border: '1px solid #30363d', borderRadius: 8, fontSize: 13, cursor: 'pointer',
        }}>
          <option value={12}>12h forecast</option>
          <option value={24}>24h forecast</option>
          <option value={48}>48h forecast</option>
        </select>
      </div>

      {predChartData.length > 0 && (
        <div style={{ background: '#161b22', border: '1px solid #21262d', borderRadius: 12, padding: '24px', marginBottom: 20 }}>
          <h2 style={{ fontSize: 14, fontWeight: 600, color: '#e2e8f0', marginBottom: 20 }}>
            Page View Forecast — Next {hours}h (with confidence bounds)
          </h2>
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={predChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
              <XAxis dataKey="hour" tick={{ fill: '#6e7681', fontSize: 10 }} label={{ value: 'Hours ahead', position: 'insideBottom', fill: '#6e7681', fontSize: 10 }} />
              <YAxis tick={{ fill: '#6e7681', fontSize: 10 }} />
              <Tooltip contentStyle={{ background: '#1e2028', border: '1px solid #30363d', borderRadius: 8, color: '#e2e8f0', fontSize: 12 }} />
              <Line type="monotone" dataKey="pred"  stroke="#52b788" strokeWidth={2.5} dot={false} name="Predicted" />
              <Line type="monotone" dataKey="upper" stroke="#52b788" strokeWidth={1} strokeDasharray="4 3" dot={false} name="Upper bound" />
              <Line type="monotone" dataKey="lower" stroke="#52b788" strokeWidth={1} strokeDasharray="4 3" dot={false} name="Lower bound" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {anomalyData.length > 0 && (
        <div style={{ background: '#161b22', border: '1px solid #21262d', borderRadius: 12, padding: '24px' }}>
          <h2 style={{ fontSize: 14, fontWeight: 600, color: '#e2e8f0', marginBottom: 20 }}>
            Anomaly Detection — Last 96 Hours (red = anomalous)
          </h2>
          <ResponsiveContainer width="100%" height={180}>
            <ScatterChart>
              <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
              <XAxis dataKey="x" tick={{ fill: '#6e7681', fontSize: 10 }} name="Hour" />
              <YAxis dataKey="y" tick={{ fill: '#6e7681', fontSize: 10 }} name="Page Views" />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ background: '#1e2028', border: '1px solid #30363d', borderRadius: 8, fontSize: 12, color: '#e2e8f0' }} />
              <Scatter data={anomalyData.filter(d => !d.anomaly)} fill="#52b788" opacity={0.4} r={2} name="Normal" />
              <Scatter data={anomalyData.filter(d => d.anomaly)}  fill="#f85149" opacity={0.9} r={5} name="Anomaly" />
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}
