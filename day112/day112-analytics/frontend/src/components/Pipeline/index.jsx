import React, { useState, useEffect, useCallback } from 'react'
import { fetchPipelineStatus, fetchEventSummary, postEvent } from '../../api/client'

const Badge = ({ status }) => {
  const colors = { running: '#52b788', stopped: '#f85149', degraded: '#f0883e' }
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 6,
      padding: '4px 12px', borderRadius: 20,
      background: `${colors[status] || '#8b949e'}22`,
      color: colors[status] || '#8b949e', fontSize: 12, fontWeight: 600
    }}>
      <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'currentColor' }} />
      {status?.toUpperCase()}
    </span>
  )
}

export default function Pipeline() {
  const [status, setStatus]   = useState(null)
  const [summary, setSummary] = useState(null)
  const [sending, setSending] = useState(false)
  const [lastEvent, setLastEvent] = useState(null)

  const refresh = useCallback(() => {
    Promise.all([fetchPipelineStatus(), fetchEventSummary()])
      .then(([s, sm]) => { setStatus(s); setSummary(sm) })
  }, [])

  useEffect(() => { refresh(); const t = setInterval(refresh, 4000); return () => clearInterval(t) }, [refresh])

  const sendTestEvent = async () => {
    setSending(true)
    try {
      const ev = await postEvent({
        event_type: 'page_view',
        user_id: `demo_user_${Date.now()}`,
        session_id: `sess_${Date.now()}`,
        page: '/demo',
        duration_ms: 1500,
        revenue: 0,
        properties: { source: 'demo' }
      })
      setLastEvent(ev)
      refresh()
    } finally { setSending(false) }
  }

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, color: '#e2e8f0' }}>Analytics Pipeline</h1>
        <p style={{ color: '#8b949e', fontSize: 13, marginTop: 4 }}>Real-time event ingestion status</p>
      </div>

      <div style={{ display: 'flex', gap: 16, marginBottom: 20 }}>
        <div style={{ background: '#161b22', border: '1px solid #21262d', borderRadius: 12, padding: '20px 24px', flex: 1 }}>
          <div style={{ fontSize: 11, color: '#8b949e', letterSpacing: '0.8px', marginBottom: 12 }}>PIPELINE STATUS</div>
          <Badge status={status?.status || 'checking'} />
          <div style={{ marginTop: 12, fontSize: 12, color: '#6e7681' }}>
            Last processed: {status?.last_processed_at ? new Date(status.last_processed_at).toLocaleTimeString() : '—'}
          </div>
        </div>
        <div style={{ background: '#161b22', border: '1px solid #21262d', borderRadius: 12, padding: '20px 24px', flex: 1 }}>
          <div style={{ fontSize: 11, color: '#8b949e', letterSpacing: '0.8px', marginBottom: 8 }}>EVENTS INGESTED</div>
          <div style={{ fontSize: 32, fontWeight: 700, color: '#52b788', fontFamily: 'JetBrains Mono' }}>
            {status?.events_ingested ?? '—'}
          </div>
        </div>
        <div style={{ background: '#161b22', border: '1px solid #21262d', borderRadius: 12, padding: '20px 24px', flex: 1 }}>
          <div style={{ fontSize: 11, color: '#8b949e', letterSpacing: '0.8px', marginBottom: 8 }}>TOTAL DB EVENTS</div>
          <div style={{ fontSize: 32, fontWeight: 700, color: '#52b788', fontFamily: 'JetBrains Mono' }}>
            {summary?.total_events ?? '—'}
          </div>
        </div>
      </div>

      {summary?.by_type && (
        <div style={{ background: '#161b22', border: '1px solid #21262d', borderRadius: 12, padding: '20px 24px', marginBottom: 20 }}>
          <div style={{ fontSize: 13, fontWeight: 600, color: '#e2e8f0', marginBottom: 16 }}>Events by Type</div>
          {Object.entries(summary.by_type).map(([type, count]) => (
            <div key={type} style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 10 }}>
              <div style={{ width: 110, fontSize: 12, color: '#8b949e' }}>{type}</div>
              <div style={{ flex: 1, background: '#21262d', borderRadius: 4, height: 8 }}>
                <div style={{
                  width: `${Math.min((count / summary.total_events) * 100, 100)}%`,
                  height: '100%', background: '#52b788', borderRadius: 4,
                }} />
              </div>
              <div style={{ width: 40, fontSize: 12, color: '#52b788', fontFamily: 'JetBrains Mono', textAlign: 'right' }}>{count}</div>
            </div>
          ))}
        </div>
      )}

      <button onClick={sendTestEvent} disabled={sending} style={{
        padding: '10px 22px', background: '#2d6a4f', color: '#d8f3dc', border: 'none',
        borderRadius: 8, cursor: 'pointer', fontSize: 13, fontWeight: 600,
      }}>
        {sending ? 'Sending...' : '⚡ Send Test Event'}
      </button>
      {lastEvent && (
        <div style={{ marginTop: 12, padding: '10px 16px', background: '#0d1117', border: '1px solid #30363d', borderRadius: 8, fontSize: 12, fontFamily: 'JetBrains Mono', color: '#52b788' }}>
          ✓ Event ingested · id: {lastEvent.id} · type: {lastEvent.event_type}
        </div>
      )}
    </div>
  )
}
