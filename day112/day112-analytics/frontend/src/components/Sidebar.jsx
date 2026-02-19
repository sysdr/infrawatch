import React from 'react'

export default function Sidebar({ views, active, onSelect }) {
  return (
    <aside style={{
      width: 220, background: '#161b22', borderRight: '1px solid #21262d',
      display: 'flex', flexDirection: 'column', padding: '24px 0',
    }}>
      <div style={{ padding: '0 20px 28px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 32, height: 32, borderRadius: 8, background: 'linear-gradient(135deg, #2d6a4f, #52b788)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 16
          }}>⬢</div>
          <div>
            <div style={{ fontSize: 13, fontWeight: 700, color: '#e2e8f0', letterSpacing: '0.5px' }}>INSIGHT</div>
            <div style={{ fontSize: 10, color: '#6e7681', letterSpacing: '1px' }}>ANALYTICS</div>
          </div>
        </div>
      </div>

      <div style={{ padding: '0 12px', fontSize: 10, color: '#6e7681', letterSpacing: '1px', marginBottom: 8 }}>
        NAVIGATION
      </div>

      {Object.entries(views).map(([key, v]) => {
        const isActive = key === active
        return (
          <button key={key} onClick={() => onSelect(key)} style={{
            display: 'flex', alignItems: 'center', gap: 12,
            padding: '10px 20px', margin: '2px 8px', border: 'none',
            borderRadius: 8, cursor: 'pointer', textAlign: 'left',
            background: isActive ? 'rgba(45,106,79,0.25)' : 'transparent',
            borderLeft: isActive ? '3px solid #52b788' : '3px solid transparent',
            color: isActive ? '#52b788' : '#8b949e',
            fontSize: 13, fontWeight: isActive ? 600 : 400,
            transition: 'all 0.15s ease',
          }}>
            <span style={{ fontSize: 16 }}>{v.icon}</span>
            {v.label}
          </button>
        )
      })}

      <div style={{ marginTop: 'auto', padding: '16px 20px', borderTop: '1px solid #21262d' }}>
        <div style={{ fontSize: 10, color: '#6e7681' }}>Day 112 · Week 11</div>
        <div style={{ fontSize: 10, color: '#52b788', marginTop: 2 }}>Analytics Integration</div>
      </div>
    </aside>
  )
}
