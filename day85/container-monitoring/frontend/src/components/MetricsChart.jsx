import React from 'react'
import { Box, Typography, Chip } from '@mui/material'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts'
import { format } from 'date-fns'

function MetricsChart({ title, data, dataKey, color, unit, icon, baseline }) {
  const currentValue = data.length > 0 ? data[data.length - 1][dataKey] : 0
  
  const chartData = data.map(d => ({
    time: format(new Date(d.timestamp), 'HH:mm:ss'),
    value: d[dataKey]
  }))

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        {icon}
        <Typography variant="h6" sx={{ ml: 1, flexGrow: 1 }}>
          {title}
        </Typography>
        <Chip
          label={`${currentValue.toFixed(1)}${unit}`}
          color={currentValue > 80 ? 'error' : currentValue > 60 ? 'warning' : 'success'}
          size="medium"
        />
      </Box>
      
      {baseline !== undefined && (
        <Typography variant="caption" color="textSecondary" display="block" sx={{ mb: 1 }}>
          Baseline: {baseline.toFixed(1)}{unit}
        </Typography>
      )}
      
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey="time"
            tick={{ fontSize: 10 }}
            interval="preserveStartEnd"
          />
          <YAxis
            domain={[0, 100]}
            tick={{ fontSize: 10 }}
            label={{ value: unit, angle: -90, position: 'insideLeft' }}
          />
          <Tooltip />
          {baseline !== undefined && (
            <ReferenceLine
              y={baseline}
              stroke="#ff9800"
              strokeDasharray="3 3"
              label={{ value: 'Baseline', position: 'right', fontSize: 10 }}
            />
          )}
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
    </Box>
  )
}

export default MetricsChart
