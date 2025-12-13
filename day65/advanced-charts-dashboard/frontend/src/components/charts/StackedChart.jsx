import React, { useState } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { Box, ToggleButtonGroup, ToggleButton } from '@mui/material';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b'];

export default function StackedChart({ data }) {
  const [chartType, setChartType] = useState('bar');

  return (
    <Box>
      <Box sx={{ mb: 2, display: 'flex', justifyContent: 'flex-end' }}>
        <ToggleButtonGroup
          value={chartType}
          exclusive
          onChange={(e, v) => v && setChartType(v)}
          size="small"
        >
          <ToggleButton value="bar">Stacked Bar</ToggleButton>
          <ToggleButton value="area">Stacked Area</ToggleButton>
        </ToggleButtonGroup>
      </Box>

      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={data.data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="category" />
          <YAxis />
          <Tooltip formatter={(value) => value.toFixed(2)} />
          <Legend />
          {data.series.map((series, idx) => (
            <Bar
              key={series}
              dataKey={series}
              stackId="a"
              fill={COLORS[idx % COLORS.length]}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </Box>
  );
}
