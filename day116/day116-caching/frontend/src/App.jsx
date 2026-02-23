import { useState, useEffect, useCallback } from 'react'
import axios from 'axios'

// Use same origin so Vite dev proxy works; set VITE_API_URL in production if API is elsewhere
const API_BASE = import.meta.env.VITE_API_URL ?? ''

const styles = {
  root: { minHeight: '100vh', background: '#0d1117', color: '#e6edf3', fontFamily: 'Inter, sans-serif', padding: 24 },
  header: { marginBottom: 24, display: 'flex', alignItems: 'center', gap: 12 },
  card: { background: '#161b22', border: '1px solid #30363d', borderRadius: 8, padding: 20, marginBottom: 16 },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 16, marginBottom: 24 },
  stat: { background: '#21262d', padding: 16, borderRadius: 8 },
  label: { fontSize: 12, color: '#8b949e', marginBottom: 4 },
  value: { fontSize: 24, fontWeight: 700, color: '#3fb950' },
  table: { width: '100%', borderCollapse: 'collapse', fontSize: 13 },
  th: { textAlign: 'left', padding: '10px 12px', borderBottom: '1px solid #30363d', color: '#8b949e', fontWeight: 600 },
  td: { padding: '10px 12px', borderBottom: '1px solid #21262d' },
  error: { color: '#f85149', marginTop: 8 },
  live: { width: 8, height: 8, borderRadius: '50%', background: '#3fb950', display: 'inline-block', marginRight: 8 },
  updated: { fontSize: 11, color: '#8b949e', marginTop: 8 },
  refreshBtn: { padding: '6px 12px', background: '#21262d', border: '1px solid #30363d', borderRadius: 6, color: '#e6edf3', cursor: 'pointer', fontSize: 12 },
  burstBtn: { padding: '8px 16px', background: '#238636', border: '1px solid #2ea043', borderRadius: 6, color: '#fff', cursor: 'pointer', fontSize: 13, fontWeight: 600 }
}

export default function App() {
  const [stats, setStats] = useState(null)
  const [keys, setKeys] = useState([])
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState(null)
  const [burstLoading, setBurstLoading] = useState(false)
  const [burstResult, setBurstResult] = useState(null)

  const fetchData = useCallback(async () => {
    try {
      const [s, k] = await Promise.all([
        axios.get(`${API_BASE}/api/cache/stats`, { timeout: 8000 }),
        axios.get(`${API_BASE}/api/cache/keys?count=50`, { timeout: 8000 })
      ])
      setStats(s.data)
      setKeys(Array.isArray(k.data?.keys) ? k.data.keys : [])
      setError(null)
      setLastUpdated(new Date())
    } catch (e) {
      setError(e.message || 'Failed to fetch — is the backend running on port 8000?')
    } finally {
      setLoading(false)
    }
  }, [])

  const runBurst = useCallback(async () => {
    setBurstLoading(true)
    setBurstResult(null)
    try {
      const r = await axios.post(`${API_BASE}/api/cache/simulate/burst?count=20`, {}, { timeout: 15000 })
      setBurstResult(r.data)
      await fetchData()
    } catch (e) {
      setError(e.message || 'Burst failed')
    } finally {
      setBurstLoading(false)
    }
  }, [fetchData])

  useEffect(() => {
    fetchData()
    const id = setInterval(fetchData, 2000)
    return () => clearInterval(id)
  }, [fetchData])

  return (
    <div style={styles.root}>
      <header style={styles.header}>
        <span style={{ ...styles.live, background: error ? '#f85149' : (stats ? '#3fb950' : '#8b949e') }} />
        <h1 style={{ margin: 0, fontSize: 24 }}>CacheOps — Day 116</h1>
        <span style={{ fontSize: 12, color: '#8b949e' }}>Redis cache dashboard</span>
        {lastUpdated && <span style={styles.updated}>Live · updated {lastUpdated.toLocaleTimeString()}</span>}
        <button type="button" style={styles.refreshBtn} onClick={() => { setLoading(true); fetchData(); }}>Refresh</button>
        <button type="button" style={styles.burstBtn} onClick={runBurst} disabled={burstLoading}>
          {burstLoading ? 'Running…' : 'Run burst (seed cache)'}
        </button>
      </header>

      {error && <div style={styles.error}>{error}</div>}

      {loading && !stats && !error && <div style={{ color: '#8b949e', padding: 24 }}>Loading…</div>}

      {stats && (
        <>
          <div style={styles.grid}>
            <div style={styles.stat}>
              <div style={styles.label}>Hit rate</div>
              <div style={{ ...styles.value, color: (stats.hit_rate || 0) > 70 ? '#3fb950' : (stats.hit_rate || 0) > 40 ? '#d29922' : '#f85149' }}>{Number(stats.hit_rate || 0).toFixed(1)}%</div>
            </div>
            <div style={styles.stat}>
              <div style={styles.label}>Hits / Misses</div>
              <div style={styles.value}>{stats.hits ?? 0} / {stats.misses ?? 0}</div>
            </div>
            <div style={styles.stat}>
              <div style={styles.label}>Avg latency</div>
              <div style={styles.value}>{Number(stats.avg_latency_ms || 0).toFixed(2)} ms</div>
            </div>
            <div style={styles.stat}>
              <div style={styles.label}>Invalidations</div>
              <div style={styles.value}>{stats.invalidations ?? 0}</div>
            </div>
            <div style={styles.stat}>
              <div style={styles.label}>Redis memory</div>
              <div style={{ ...styles.value, fontSize: 16 }}>{stats.redis_info?.used_memory_human ?? '—'}</div>
            </div>
          </div>
          {lastUpdated && <div style={styles.updated}>Data refreshes every 2s · last updated {lastUpdated.toLocaleTimeString()}</div>}
          {burstResult && (
            <div style={{ ...styles.card, borderColor: '#238636' }}>
              Last burst: <strong>{burstResult.hit_rate?.toFixed(1)}%</strong> hit rate, {burstResult.burst_results?.length ?? 0} requests, avg latency <strong>{burstResult.avg_latency_ms?.toFixed(2)} ms</strong>. Stats above update every 2s.
            </div>
          )}

          <div style={styles.card}>
            <h2 style={{ margin: '0 0 12px', fontSize: 16 }}>Cache keys ({keys.length})</h2>
            <table style={styles.table}>
              <thead>
                <tr>
                  <th style={styles.th}>Key</th>
                  <th style={styles.th}>TTL</th>
                  <th style={styles.th}>Size</th>
                </tr>
              </thead>
              <tbody>
                {keys.slice(0, 20).map((k, i) => (
                  <tr key={k.key + i}>
                    <td style={{ ...styles.td, fontFamily: 'monospace', color: '#58a6ff' }}>{k.key}</td>
                    <td style={styles.td}>{k.ttl >= 0 ? `${k.ttl}s` : '∞'}</td>
                    <td style={styles.td}>{k.size_bytes ? `${k.size_bytes}B` : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {keys.length === 0 && <div style={{ color: '#8b949e', padding: 16 }}>No keys. Use API or run burst demo.</div>}
          </div>
        </>
      )}
    </div>
  )
}
