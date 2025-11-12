import React from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

function MetricsChart({ title, data, dataKey, color, unit }) {
  const getValue = (obj, path) => {
    return path.split('.').reduce((acc, part) => acc?.[part], obj)
  }

  const chartData = data.map(item => ({
    timestamp: new Date(item.timestamp * 1000).toLocaleTimeString(),
    value: getValue(item, dataKey) || 0
  }))

  const latestValue = chartData.length > 0 ? chartData[chartData.length - 1].value : 0

  return (
    <div className="chart-container">
      <div className="chart-header">
        <h3>{title}</h3>
        <div className="chart-value" style={{ color }}>
          {latestValue.toFixed(1)}{unit}
        </div>
      </div>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            dataKey="timestamp" 
            tick={{ fontSize: 12 }}
            interval="preserveStartEnd"
          />
          <YAxis 
            tick={{ fontSize: 12 }}
            domain={[0, 100]}
          />
          <Tooltip />
          <Line 
            type="monotone" 
            dataKey="value" 
            stroke={color} 
            strokeWidth={2}
            dot={false}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export default MetricsChart
