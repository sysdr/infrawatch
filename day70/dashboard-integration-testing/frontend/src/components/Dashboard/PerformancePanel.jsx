import React from 'react';
import { Paper, Grid, Box, Typography } from '@mui/material';
import PeopleIcon from '@mui/icons-material/People';
import SpeedIcon from '@mui/icons-material/Speed';
import MemoryIcon from '@mui/icons-material/Memory';
import TimerIcon from '@mui/icons-material/Timer';

export default function PerformancePanel({ stats }) {
  if (!stats) {
    return null;
  }

  const StatCard = ({ icon, label, value, unit }) => (
    <Paper sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
      <Box sx={{ color: 'primary.main' }}>
        {icon}
      </Box>
      <Box>
        <Typography variant="body2" color="text.secondary">
          {label}
        </Typography>
        <Typography variant="h5" component="div">
          {value} <Typography component="span" variant="body2">{unit}</Typography>
        </Typography>
      </Box>
    </Paper>
  );

  return (
    <Grid container spacing={2}>
      <Grid item xs={6} sm={3}>
        <StatCard
          icon={<PeopleIcon />}
          label="Connected Clients"
          value={stats.connected_clients}
          unit=""
        />
      </Grid>
      <Grid item xs={6} sm={3}>
        <StatCard
          icon={<SpeedIcon />}
          label="Metrics/Second"
          value={stats.metrics_per_second}
          unit="m/s"
        />
      </Grid>
      <Grid item xs={6} sm={3}>
        <StatCard
          icon={<MemoryIcon />}
          label="Memory Usage"
          value={stats.memory_usage_mb}
          unit="MB"
        />
      </Grid>
      <Grid item xs={6} sm={3}>
        <StatCard
          icon={<TimerIcon />}
          label="Uptime"
          value={Math.floor(stats.uptime_seconds)}
          unit="sec"
        />
      </Grid>
    </Grid>
  );
}
