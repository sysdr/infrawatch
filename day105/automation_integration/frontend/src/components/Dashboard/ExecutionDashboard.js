import React, { useState, useEffect } from 'react';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import PendingIcon from '@mui/icons-material/Pending';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

import { executionsApi, monitoringApi } from '../../services/api';

function ExecutionDashboard() {
  const [metrics, setMetrics] = useState(null);
  const [recentExecutions, setRecentExecutions] = useState([]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [metricsRes, executionsRes, healthRes] = await Promise.all([
        monitoringApi.getMetrics(),
        executionsApi.list(),
        monitoringApi.getHealth().catch(() => ({ data: null })),
      ]);
      setMetrics({ ...metricsRes.data, health: healthRes.data });
      setRecentExecutions(executionsRes.data.slice(0, 10));
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    }
  };

  if (!metrics) {
    return <Typography>Loading...</Typography>;
  }

  const chartData = recentExecutions.map((exec, index) => ({
    name: `Exec ${exec.id}`,
    time: exec.execution_time || 0,
  }));

  return (
    <Grid container spacing={3}>
      {/* Metrics Cards */}
      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ bgcolor: '#e3f2fd' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Total Executions
                </Typography>
                <Typography variant="h4">{metrics.total_executions}</Typography>
              </Box>
              <PlayArrowIcon sx={{ fontSize: 48, color: '#1976d2' }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ bgcolor: '#e8f5e9' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Completed
                </Typography>
                <Typography variant="h4">{metrics.completed}</Typography>
              </Box>
              <CheckCircleIcon sx={{ fontSize: 48, color: '#4caf50' }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ bgcolor: '#ffebee' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Failed
                </Typography>
                <Typography variant="h4">{metrics.failed}</Typography>
              </Box>
              <ErrorIcon sx={{ fontSize: 48, color: '#f44336' }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ bgcolor: '#fff3e0' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Success Rate
                </Typography>
                <Typography variant="h4">{(metrics.success_rate ?? 0).toFixed(1)}%</Typography>
              </Box>
              <CheckCircleIcon sx={{ fontSize: 48, color: '#ff9800' }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Execution Time Chart */}
      <Grid item xs={12}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Recent Execution Times
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis label={{ value: 'Time (s)', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="time" stroke="#1976d2" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </Paper>
      </Grid>

      {/* Additional Metrics */}
      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Performance Metrics
          </Typography>
          <Box sx={{ mt: 2 }}>
            <Typography variant="body1">
              Average Execution Time: <strong>{(metrics.average_execution_time ?? 0).toFixed(2)}s</strong>
            </Typography>
            <Typography variant="body1" sx={{ mt: 1 }}>
              Running: <strong>{metrics.running}</strong>
            </Typography>
            <Typography variant="body1" sx={{ mt: 1 }}>
              Pending: <strong>{metrics.pending}</strong>
            </Typography>
          </Box>
        </Paper>
      </Grid>

      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            System Status
          </Typography>
          <Box sx={{ mt: 2 }}>
            <Typography variant="body1">
              Status: <strong style={{ color: metrics.health?.status === 'healthy' ? '#4caf50' : '#f44336' }}>{metrics.health?.status ?? 'Loading...'}</strong>
            </Typography>
            <Typography variant="body1" sx={{ mt: 1 }}>
              Active Workers: <strong>{metrics.health?.active_workers ?? '-'}</strong>
            </Typography>
            <Typography variant="body1" sx={{ mt: 1 }}>
              Queue Size: <strong>{metrics.health?.queue_size ?? '-'}</strong>
            </Typography>
          </Box>
        </Paper>
      </Grid>
    </Grid>
  );
}

export default ExecutionDashboard;
