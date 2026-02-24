import React from 'react';

export function GaugeChart({ value = 0, max = 100, label, color }) {
  const pct = Math.min(value / max, 1);
  const angle = pct * 180;
  const r = 50;
  const cx = 70, cy = 70;

  // Arc path
  const toRad = (deg) => (deg - 180) * Math.PI / 180;
  const x1 = cx + r * Math.cos(toRad(0));
  const y1 = cy + r * Math.sin(toRad(0));
  const x2 = cx + r * Math.cos(toRad(angle));
  const y2 = cy + r * Math.sin(toRad(angle));
  const largeArc = angle > 90 ? 1 : 0;

  const gaugeColor = value < 60 ? '#4caf50' : value < 80 ? '#ff9800' : '#f44336';

  return (
    <div style={{ textAlign: 'center', padding: '8px' }}>
      <svg width="140" height="90" viewBox="0 0 140 90">
        {/* Background arc */}
        <path
          d={`M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`}
          fill="none" stroke="#1e293b" strokeWidth="12" strokeLinecap="round"
        />
        {/* Value arc */}
        {pct > 0 && (
          <path
            d={`M ${cx - r} ${cy} A ${r} ${r} 0 ${largeArc} 1 ${x2} ${y2}`}
            fill="none" stroke={gaugeColor} strokeWidth="12" strokeLinecap="round"
          />
        )}
        <text x={cx} y={cy - 4} textAnchor="middle" fill={gaugeColor} fontSize="18" fontWeight="700">
          {Math.round(value)}%
        </text>
        <text x={cx} y={cy + 14} textAnchor="middle" fill="#94a3b8" fontSize="9">
          {label}
        </text>
      </svg>
    </div>
  );
}
