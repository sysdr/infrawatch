import { useState, useEffect } from 'react';
import { Grid, Card, CardContent, Typography, Box, CircularProgress } from '@mui/material';
import { CheckCircle, Error, HourglassEmpty, TrendingUp } from '@mui/icons-material';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { api } from '../services/api';
import type { Stats } from '../types';

const COLORS = ['#4caf50', '#ff9800', '#f44336', '#2196f3'];

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadStats();
    const interval = setInterval(loadStats, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadStats = async () => {
    try {
      const { data } = await api.getStats();
      setStats(data);
      setError(null);
    } catch (e) {
      setError('Cannot connect to API. Start the backend server.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={4}>
        <Typography color="error">{error}</Typography>
        <Typography variant="body2" sx={{ mt: 1 }}>
          Run: cd backend && python init_db.py && uvicorn app.main:app --port 8000
        </Typography>
      </Box>
    );
  }

  if (!stats) return null;

  let chartData = [
    { name: 'Completed', value: stats.completed },
    { name: 'Pending', value: stats.pending },
    { name: 'Failed', value: stats.failed },
  ].filter(d => d.value > 0);

  if (chartData.length === 0) {
    chartData = [{ name: 'No data yet', value: 1 }];
  }

  const hasData = stats.total_actions > 0;

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={3}>
        <Card sx={{ bgcolor: '#e3f2fd', borderLeft: 4, borderColor: '#2196f3' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>Total Actions</Typography>
                <Typography variant="h4">{stats.total_actions}</Typography>
              </Box>
              <TrendingUp sx={{ fontSize: 48, color: '#2196f3', opacity: 0.7 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card sx={{ bgcolor: '#fff3e0', borderLeft: 4, borderColor: '#ff9800' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>Pending Approval</Typography>
                <Typography variant="h4">{stats.pending}</Typography>
              </Box>
              <HourglassEmpty sx={{ fontSize: 48, color: '#ff9800', opacity: 0.7 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card sx={{ bgcolor: '#e8f5e9', borderLeft: 4, borderColor: '#4caf50' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>Completed</Typography>
                <Typography variant="h4">{stats.completed}</Typography>
              </Box>
              <CheckCircle sx={{ fontSize: 48, color: '#4caf50', opacity: 0.7 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card sx={{ bgcolor: '#ffebee', borderLeft: 4, borderColor: '#f44336' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>Success Rate</Typography>
                <Typography variant="h4">{stats.success_rate}%</Typography>
              </Box>
              <Error sx={{ fontSize: 48, color: '#f44336', opacity: 0.7 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Actions Distribution</Typography>
            {!hasData && (
              <Typography color="textSecondary" sx={{ mb: 2 }}>
                Run the demo script (./demo.sh) to populate data and see metrics update.
              </Typography>
            )}
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie data={chartData} cx="50%" cy="50%" labelLine={false} outerRadius={100} fill="#8884d8" dataKey="value">
                  {chartData.map((entry, index) => (
                    <Cell key={index} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}
