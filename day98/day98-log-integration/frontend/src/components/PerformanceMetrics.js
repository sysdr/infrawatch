import React, { useState, useEffect } from 'react';
import {
  Paper,
  Typography,
  Box,
  Grid,
  Card,
  CardContent
} from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

function PerformanceMetrics() {
  const [metrics, setMetrics] = useState({
    websocket_connections: 0,
    logs_ingested_total: 0,
    logs_indexed_total: 0,
    alerts_triggered_total: 0
  });
  const [metricsHistory, setMetricsHistory] = useState([]);

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchMetrics = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/metrics`);
      const newMetrics = response.data;

      setMetrics(newMetrics);

      setMetricsHistory(prev => {
        const newHistory = [
          ...prev,
          {
            timestamp: new Date().toLocaleTimeString(),
            ingested: parseInt(newMetrics.logs_ingested_total) || 0,
            indexed: parseInt(newMetrics.logs_indexed_total) || 0
          }
        ];
        return newHistory.slice(-20);
      });
    } catch (error) {
      console.error('Error fetching metrics:', error);
    }
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>Performance Metrics</Typography>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                WebSocket Connections
              </Typography>
              <Typography variant="h4">
                {metrics.websocket_connections}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Logs Ingested
              </Typography>
              <Typography variant="h4">
                {metrics.logs_ingested_total}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Logs Indexed
              </Typography>
              <Typography variant="h4">
                {metrics.logs_indexed_total}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Alerts Triggered
              </Typography>
              <Typography variant="h4">
                {metrics.alerts_triggered_total}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Paper sx={{ p: 2 }}>
        <Typography variant="subtitle1" gutterBottom>
          Log Processing Throughput
        </Typography>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={metricsHistory}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="timestamp" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="ingested" stroke="#8884d8" name="Ingested" />
            <Line type="monotone" dataKey="indexed" stroke="#82ca9d" name="Indexed" />
          </LineChart>
        </ResponsiveContainer>
      </Paper>
    </Box>
  );
}

export default PerformanceMetrics;
