import React from 'react';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ZAxis
} from 'recharts';
import { Box, Typography, Chip } from '@mui/material';

export default function ScatterPlot({ data }) {
  const normalPoints = data.data.filter(p => !p.outlier);
  const outlierPoints = data.data.filter(p => p.outlier);

  return (
    <Box>
      <Box sx={{ mb: 2, display: 'flex', gap: 2, alignItems: 'center' }}>
        <Typography variant="body2">
          Correlation Coefficient: <strong>{data.correlation.toFixed(3)}</strong>
        </Typography>
        <Chip label={`${data.outliers} Outliers`} size="small" color="warning" />
      </Box>

      <ResponsiveContainer width="100%" height={400}>
        <ScatterChart margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" dataKey="x" name={data.x_metric} />
          <YAxis type="number" dataKey="y" name={data.y_metric} />
          <ZAxis range={[60, 60]} />
          <Tooltip cursor={{ strokeDasharray: '3 3' }} />
          <Scatter
            name="Normal"
            data={normalPoints}
            fill="#3b82f6"
            opacity={0.6}
          />
          <Scatter
            name="Outliers"
            data={outlierPoints}
            fill="#ef4444"
            opacity={0.8}
          />
        </ScatterChart>
      </ResponsiveContainer>
    </Box>
  );
}
