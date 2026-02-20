import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Paper, Typography } from '@mui/material';

export default function LatencyChart({ history }) {
  return (
    <Paper elevation={0} sx={{ p: 2.5, borderRadius: 3, border: '1px solid #e8f5e9', height: 280 }}>
      <Typography variant="subtitle2" fontWeight={700} color="#2e7d32" gutterBottom>
        Request Latency (ms)
      </Typography>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={history} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f8e9" />
          <XAxis dataKey="time" tick={{ fontSize: 10, fill: '#66bb6a' }} />
          <YAxis unit="ms" tick={{ fontSize: 10, fill: '#66bb6a' }} />
          <Tooltip contentStyle={{ borderRadius: 8, border: '1px solid #c8e6c9', fontSize: 12 }} />
          <Legend wrapperStyle={{ fontSize: 11 }} />
          <Line type="monotone" dataKey="p50" stroke="#66bb6a" strokeWidth={2} dot={false} name="p50" />
          <Line type="monotone" dataKey="p95" stroke="#26a69a" strokeWidth={2} dot={false} name="p95" />
          <Line type="monotone" dataKey="p99" stroke="#1b5e20" strokeWidth={2.5} dot={false} name="p99" />
        </LineChart>
      </ResponsiveContainer>
    </Paper>
  );
}
