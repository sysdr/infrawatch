import React, { useState, useEffect } from 'react';
import {
  Box, Paper, Typography, Grid, Card, CardContent, CircularProgress,
  Alert, Button
} from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import RefreshIcon from '@mui/icons-material/Refresh';
import { dashboardAPI } from '../../services/api';

const MetricCard = ({ title, value, subtitle }) => (
  <Card sx={{ minHeight: 120 }}>
    <CardContent>
      <Typography color="text.secondary" gutterBottom variant="body2">
        {title}
      </Typography>
      <Typography variant="h4" component="div" sx={{ fontWeight: 600 }}>
        {value}
      </Typography>
      {subtitle && (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
          {subtitle}
        </Typography>
      )}
    </CardContent>
  </Card>
);

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await dashboardAPI.getStats();
      setStats(res.data);
    } catch (err) {
      setError('Failed to load dashboard. Is the backend running on port 8000?');
      setStats({
        templates: 0,
        reports: 0,
        schedules: 0,
        distribution_lists: 0,
        executions_total: 0,
        executions_completed: 0,
        executions_failed: 0,
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStats();
    const interval = setInterval(loadStats, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading && !stats) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={200}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <DashboardIcon /> Reporting metrics
        </Typography>
        <Button startIcon={<RefreshIcon />} onClick={loadStats} size="small">
          Refresh
        </Button>
      </Box>
      {error && (
        <Alert severity="warning" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={4}>
          <MetricCard title="Templates" value={stats?.templates ?? 0} subtitle="Active report templates" />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <MetricCard title="Reports" value={stats?.reports ?? 0} subtitle="Report definitions" />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <MetricCard title="Schedules" value={stats?.schedules ?? 0} subtitle="Active schedules" />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <MetricCard title="Distribution lists" value={stats?.distribution_lists ?? 0} subtitle="Recipient lists" />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <MetricCard title="Executions (total)" value={stats?.executions_total ?? 0} subtitle="Report runs" />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="Executions (completed)"
            value={stats?.executions_completed ?? 0}
            subtitle={stats?.executions_failed ? `Failed: ${stats.executions_failed}` : null}
          />
        </Grid>
      </Grid>
      <Paper sx={{ p: 2, mt: 3 }}>
        <Typography variant="subtitle2" color="text.secondary">
          Demo: Create a template (Templates), then a report (Report Builder), then click Generate. Dashboard values update automatically.
        </Typography>
      </Paper>
    </Box>
  );
}
