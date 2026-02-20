import React from 'react';
import { Paper, Typography, Box, LinearProgress } from '@mui/material';

export default function SystemPanel({ data }) {
  if (!data) return null;
  const { system } = data;
  const cpuColor = system.cpu_pct > 80 ? '#c62828' : '#2e7d32';
  const memColor = system.mem_used_pct > 80 ? '#c62828' : '#26a69a';
  return (
    <Paper elevation={0} sx={{ p: 2.5, borderRadius: 3, border: '1px solid #e8f5e9' }}>
      <Typography variant="subtitle2" fontWeight={700} color="#2e7d32" gutterBottom>
        System Resources
      </Typography>
      {[
        { label: 'CPU', value: system.cpu_pct, color: cpuColor },
        { label: 'Memory', value: system.mem_used_pct, color: memColor },
      ].map(({ label, value, color }) => (
        <Box key={label} mb={1.5}>
          <Box display="flex" justifyContent="space-between">
            <Typography variant="caption" color="text.secondary">{label}</Typography>
            <Typography variant="caption" fontWeight={700} color={color}>{value}%</Typography>
          </Box>
          <LinearProgress variant="determinate" value={value} sx={{
            height: 8, borderRadius: 4, bgcolor: '#e8f5e9',
            '& .MuiLinearProgress-bar': { bgcolor: color, borderRadius: 4 },
          }} />
        </Box>
      ))}
      <Typography variant="caption" color="text.secondary">
        Memory free: {system.mem_available_mb} MB
      </Typography>
    </Paper>
  );
}
