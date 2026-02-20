import React from 'react';
import { Paper, Typography, Box, LinearProgress, Chip } from '@mui/material';

export default function PoolPanel({ data }) {
  if (!data) return null;
  const { pool } = data;
  const util = pool.utilisation_pct;
  const barColor = util > 80 ? '#c62828' : util > 60 ? '#f57f17' : '#2e7d32';
  return (
    <Paper elevation={0} sx={{ p: 2.5, borderRadius: 3, border: '1px solid #e8f5e9' }}>
      <Typography variant="subtitle2" fontWeight={700} color="#2e7d32" gutterBottom>
        Connection Pool
      </Typography>
      <Box display="flex" gap={1} flexWrap="wrap" mb={1.5}>
        <Chip label={`Pool Size: ${pool.pool_size}`} size="small" sx={{ bgcolor: '#e8f5e9' }} />
        <Chip label={`Checked Out: ${pool.checked_out}`} size="small" sx={{ bgcolor: '#e0f2f1' }} />
        <Chip label={`Available: ${pool.checked_in}`} size="small" sx={{ bgcolor: '#f1f8e9' }} />
      </Box>
      <Typography variant="caption" color="text.secondary">Utilisation</Typography>
      <Box display="flex" alignItems="center" gap={1} mt={0.5}>
        <LinearProgress variant="determinate" value={util} sx={{
          flex: 1, height: 10, borderRadius: 5, bgcolor: '#e8f5e9',
          '& .MuiLinearProgress-bar': { bgcolor: barColor, borderRadius: 5 },
        }} />
        <Typography variant="body2" fontWeight={700} color={barColor}>{util}%</Typography>
      </Box>
    </Paper>
  );
}
