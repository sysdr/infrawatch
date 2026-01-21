import React, { useState, useEffect } from 'react';
import {
  Paper,
  Grid,
  Typography,
  Box,
  LinearProgress
} from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { healthApi } from '../../services/api';
import dayjs from 'dayjs';

function HealthView({ wsData }) {
  const [currentHealth, setCurrentHealth] = useState(null);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (wsData && wsData.type === 'health_update') {
      setCurrentHealth(wsData.data);
    }
  }, [wsData]);

  const fetchHealth = async () => {
    try {
      const [current, hist] = await Promise.all([
        healthApi.getCurrent(),
        healthApi.getHistory(1)
      ]);
      setCurrentHealth(current.data);
      setHistory(hist.data.map(h => ({
        ...h,
        time: dayjs(h.timestamp).format('HH:mm:ss')
      })));
    } catch (error) {
      console.error('Error fetching health:', error);
    }
  };

  const HealthBar = ({ label, value }) => (
    <Box sx={{ mb: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
        <Typography variant="body2">{label}</Typography>
        <Typography variant="body2" fontWeight="bold">
          {value ? Math.round(value) : 0}%
        </Typography>
      </Box>
      <LinearProgress
        variant="determinate"
        value={value || 0}
        sx={{
          height: 10,
          borderRadius: 5,
          bgcolor: 'grey.300',
          '& .MuiLinearProgress-bar': {
            bgcolor: value >= 80 ? 'success.main' : value >= 60 ? 'warning.main' : 'error.main'
          }
        }}
      />
    </Box>
  );

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Cluster Health
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Health Components
            </Typography>
            <HealthBar label="Node Health" value={currentHealth?.node_health_score} />
            <HealthBar label="Pod Health" value={currentHealth?.pod_health_score} />
            <HealthBar label="Resource Health" value={currentHealth?.resource_health_score} />
            <HealthBar label="Deployment Health" value={currentHealth?.deployment_health_score} />
            <HealthBar label="API Latency" value={currentHealth?.api_latency_score} />
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Cluster Statistics
            </Typography>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Typography>Total Nodes:</Typography>
              <Typography fontWeight="bold">{currentHealth?.stats?.total_nodes || 0}</Typography>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Typography>Ready Nodes:</Typography>
              <Typography fontWeight="bold" color="success.main">
                {currentHealth?.stats?.ready_nodes || 0}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Typography>Total Pods:</Typography>
              <Typography fontWeight="bold">{currentHealth?.stats?.total_pods || 0}</Typography>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Typography>Running Pods:</Typography>
              <Typography fontWeight="bold" color="success.main">
                {currentHealth?.stats?.running_pods || 0}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Typography>Failed Pods:</Typography>
              <Typography fontWeight="bold" color="error.main">
                {currentHealth?.stats?.failed_pods || 0}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography>Pending Pods:</Typography>
              <Typography fontWeight="bold" color="warning.main">
                {currentHealth?.stats?.pending_pods || 0}
              </Typography>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Health Score Trend (Last Hour)
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={history}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="overall_score" stroke="#326ce5" name="Overall" strokeWidth={2} />
                <Line type="monotone" dataKey="node_health" stroke="#4caf50" name="Nodes" />
                <Line type="monotone" dataKey="pod_health" stroke="#ff9800" name="Pods" />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default HealthView;
