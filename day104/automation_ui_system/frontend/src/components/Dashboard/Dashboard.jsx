import React, { useState, useEffect } from 'react';
import { Box, Grid, Paper, Typography, Card, CardContent, CircularProgress, Chip } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import AssessmentIcon from '@mui/icons-material/Assessment';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { analyticsApi, executionApi } from '../../services/api';
import wsService from '../../services/websocket';

const COLORS = ['#4caf50', '#f44336', '#2196f3', '#ff9800'];

const Dashboard = () => {
  const [analytics, setAnalytics] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [recentExecutions, setRecentExecutions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
    wsService.connect();
    wsService.on('workflow_update', () => loadData());
    const pollInterval = setInterval(loadData, 5000);
    return () => {
      wsService.off('workflow_update', loadData);
      clearInterval(pollInterval);
    };
  }, []);

  const loadData = async () => {
    try {
      const [analyticsRes, timelineRes, executionsRes] = await Promise.all([
        analyticsApi.getOverview(),
        analyticsApi.getTimeline(7),
        executionApi.getAll(),
      ]);
      setAnalytics(analyticsRes.data);
      setTimeline(Object.entries(timelineRes.data.timeline || {}).map(([date, statuses]) => ({
        date,
        success: statuses.success || 0,
        failed: statuses.failed || 0,
        running: statuses.running || 0,
      })));
      setRecentExecutions((executionsRes.data.executions || []).slice(0, 10));
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}><CircularProgress /></Box>;

  const statusDistribution = analytics ? [
    { name: 'Success', value: analytics.success_count || 0 },
    { name: 'Failed', value: analytics.failed_count || 0 },
    { name: 'Running', value: analytics.running_count || 0 },
  ].filter((d) => d.value > 0) : [];

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>Automation Dashboard</Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: '#e3f2fd' }}><CardContent>
            <Typography color="textSecondary" gutterBottom>Total Workflows</Typography>
            <Typography variant="h3">{analytics?.total_workflows ?? 0}</Typography>
          </CardContent></Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: '#e8f5e9' }}><CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}><CheckCircleIcon color="success" /><Typography color="textSecondary" gutterBottom>Success Rate</Typography></Box>
            <Typography variant="h3">{analytics?.success_rate ?? 0}%</Typography>
          </CardContent></Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: '#fce4ec' }}><CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}><ErrorIcon color="error" /><Typography color="textSecondary" gutterBottom>Failed Executions</Typography></Box>
            <Typography variant="h3">{analytics?.failed_count ?? 0}</Typography>
          </CardContent></Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: '#fff3e0' }}><CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}><AssessmentIcon color="primary" /><Typography color="textSecondary" gutterBottom>Avg Duration</Typography></Box>
            <Typography variant="h3">{analytics?.avg_duration_seconds != null ? `${Number(analytics.avg_duration_seconds).toFixed(1)}s` : '0s'}</Typography>
          </CardContent></Card>
        </Grid>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Execution Timeline (Last 7 Days)</Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={timeline}>
                <CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="date" /><YAxis /><Tooltip /><Legend />
                <Line type="monotone" dataKey="success" stroke="#4caf50" strokeWidth={2} />
                <Line type="monotone" dataKey="failed" stroke="#f44336" strokeWidth={2} />
                <Line type="monotone" dataKey="running" stroke="#2196f3" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Status Distribution</Typography>
            <ResponsiveContainer width="100%" height={300}>
              {statusDistribution.length ? (
                <PieChart><Pie data={statusDistribution} cx="50%" cy="50%" labelLine={false} label={(e) => e.name} outerRadius={80} fill="#8884d8" dataKey="value">
                  {statusDistribution.map((entry, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie><Tooltip /></PieChart>
              ) : <Typography>No execution data yet. Run a workflow to see distribution.</Typography>}
            </ResponsiveContainer>
          </Paper>
        </Grid>
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Recent Executions</Typography>
            {recentExecutions.length ? recentExecutions.map((exec) => (
              <Box key={exec.id} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', p: 2, border: '1px solid #e0e0e0', borderRadius: 1, mb: 1 }}>
                <Box>
                  <Typography variant="body1">Execution #{exec.id}</Typography>
                  <Typography variant="body2" color="textSecondary">Workflow ID: {exec.workflow_id} • {exec.trigger_type}</Typography>
                </Box>
                <Chip label={exec.status} color={exec.status === 'success' ? 'success' : exec.status === 'failed' ? 'error' : 'default'} size="small" />
              </Box>
            )) : <Typography color="textSecondary">No executions yet. Create and run a workflow from Workflow Builder.</Typography>}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
