import React, { useEffect, useState } from 'react';
import { Box, Paper, Typography, Grid, Card, CardContent, CircularProgress } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { costsAPI } from '../services/api';

const COLORS = ['#4caf50', '#2196f3', '#ff9800', '#f44336', '#9c27b0'];

function CostDashboard() {
  const [summary, setSummary] = useState(null);
  const [trends, setTrends] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [summaryRes, trendsRes, forecastRes] = await Promise.all([
        costsAPI.getSummary(30),
        costsAPI.getTrends(90),
        costsAPI.getForecast(30)
      ]);
      
      setSummary(summaryRes.data);
      setTrends(trendsRes.data);
      setForecast(forecastRes.data);
    } catch (error) {
      console.error('Failed to load cost data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Cost Analysis
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card elevation={3}>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Total Spend (30 days)
              </Typography>
              <Typography variant="h3" color="primary">
                ${summary?.total?.toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card elevation={3}>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Daily Average
              </Typography>
              <Typography variant="h3" color="success.main">
                ${trends?.mean?.toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card elevation={3}>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Anomalies Detected
              </Typography>
              <Typography variant="h3" color="warning.main">
                {trends?.anomalies?.length || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={8}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Cost Trends (90 days)
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trends?.daily_costs || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date" 
                  tickFormatter={(val) => new Date(val).toLocaleDateString()}
                />
                <YAxis />
                <Tooltip 
                  formatter={(value) => `$${value.toFixed(2)}`}
                  labelFormatter={(label) => new Date(label).toLocaleDateString()}
                />
                <Legend />
                <Line type="monotone" dataKey="amount" stroke="#2196f3" name="Daily Cost" />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Cost by Provider
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={summary?.by_provider || []}
                  dataKey="amount"
                  nameKey="provider"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label={(entry) => `${entry.provider}: $${entry.amount.toFixed(0)}`}
                >
                  {(summary?.by_provider || []).map((entry, index) => (
                    <Cell key={index} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Cost Forecast (30 days)
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={forecast?.forecast || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date"
                  tickFormatter={(val) => new Date(val).toLocaleDateString()}
                />
                <YAxis />
                <Tooltip 
                  formatter={(value) => `$${value.toFixed(2)}`}
                  labelFormatter={(label) => new Date(label).toLocaleDateString()}
                />
                <Legend />
                <Line type="monotone" dataKey="predicted_amount" stroke="#4caf50" name="Forecast" />
                <Line type="monotone" dataKey="upper_bound" stroke="#ff9800" strokeDasharray="3 3" name="Upper Bound" />
                <Line type="monotone" dataKey="lower_bound" stroke="#ff9800" strokeDasharray="3 3" name="Lower Bound" />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Cost by Service Type
            </Typography>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={summary?.by_service || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="service" />
                <YAxis />
                <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
                <Bar dataKey="amount" fill="#2196f3" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default CostDashboard;
