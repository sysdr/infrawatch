import React from 'react';
import { Paper, Typography, Box, LinearProgress } from '@mui/material';

export default function StatCard({ title, value, unit, max, color = '#2e7d32', subtitle }) {
  const pct = max ? Math.min((parseFloat(value) / max) * 100, 100) : null;
  return (
    <Paper elevation={0} sx={{
      p: 2.5, borderRadius: 3, border: '1px solid #e8f5e9',
      background: 'linear-gradient(135deg, #f9fff9 0%, #f1f8e9 100%)',
      height: '100%',
    }}>
      <Typography variant="caption" color="text.secondary" fontWeight={600}
        textTransform="uppercase" letterSpacing={0.8}>
        {title}
      </Typography>
      <Box display="flex" alignItems="baseline" gap={0.5} mt={0.5}>
        <Typography variant="h4" fontWeight={800} color={color}>{value ?? '—'}</Typography>
        <Typography variant="body2" color="text.secondary">{unit}</Typography>
      </Box>
      {subtitle && <Typography variant="caption" color="text.secondary">{subtitle}</Typography>}
      {pct !== null && (
        <Box mt={1}>
          <LinearProgress variant="determinate" value={pct} sx={{
            height: 6, borderRadius: 3, bgcolor: '#e8f5e9',
            '& .MuiLinearProgress-bar': { bgcolor: color, borderRadius: 3 },
          }} />
        </Box>
      )}
    </Paper>
  );
}
