import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Box,
  Chip,
  LinearProgress
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { apiService } from '../services/apiService';

const COLORS = ['#0073aa', '#00a0d2', '#ff6b35', '#f7931e'];

function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [metricsData, rulesData] = await Promise.all([
          apiService.getEvaluationMetrics(),
          apiService.getAlertRules()
        ]);
        setMetrics(metricsData);
        setRules(rulesData);
      } catch (error) {
        console.error('Failed to fetch data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 30000); // Update every 30s
    return () => clearInterval(interval);
  }, []);


  if (loading || !metrics) {
    return <LinearProgress />;
  }


  const performanceData = [
    { time: '5m ago', evaluations: 4500 },
    { time: '4m ago', evaluations: 4800 },
    { time: '3m ago', evaluations: 4200 },
    { time: '2m ago', evaluations: 5100 },
    { time: '1m ago', evaluations: 4700 },
    { time: 'now', evaluations: Math.round(metrics.rules_evaluated_per_second * 60) }
  ];

  const alertDistribution = [
    { name: 'Threshold', value: 60, color: COLORS[0] },
    { name: 'Anomaly', value: 25, color: COLORS[1] },
    { name: 'Composite', value: 15, color: COLORS[2] }
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Evaluation Engine Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        {/* Key Metrics */}
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Rules/Second
              </Typography>
              <Typography variant="h4" color="primary">
                {Math.round(metrics.rules_evaluated_per_second)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Avg Latency
              </Typography>
              <Typography variant="h4" color="primary">
                {Math.round(metrics.evaluation_latency_ms)}ms
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Alerts/Hour
              </Typography>
              <Typography variant="h4" color="secondary">
                {metrics.alerts_generated_last_hour}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Rules
              </Typography>
              <Typography variant="h4" color="primary">
                {rules.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Engine Status
              </Typography>
              <Chip 
                label={metrics.engine_status.toUpperCase()}
                color="success"
                variant="outlined"
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Performance Chart */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Evaluation Performance
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={performanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="evaluations" 
                  stroke="#0073aa" 
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Alert Distribution */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Alert Types
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={alertDistribution}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  dataKey="value"
                  label={({name, value}) => `${name}: ${value}%`}
                >
                  {alertDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Quality Metrics */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Detection Quality
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <Box>
                  <Typography variant="body2" color="textSecondary">
                    False Positive Rate
                  </Typography>
                  <Typography variant="h5">
                    {(metrics.false_positive_rate * 100).toFixed(1)}%
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={metrics.false_positive_rate * 100}
                    color="warning"
                    sx={{ mt: 1 }}
                  />
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box>
                  <Typography variant="body2" color="textSecondary">
                    Deduplication Rate
                  </Typography>
                  <Typography variant="h5">
                    {(metrics.deduplication_rate * 100).toFixed(1)}%
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={metrics.deduplication_rate * 100}
                    color="info"
                    sx={{ mt: 1 }}
                  />
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box>
                  <Typography variant="body2" color="textSecondary">
                    Anomaly Detection Accuracy
                  </Typography>
                  <Typography variant="h5">
                    {(metrics.anomaly_detection_accuracy * 100).toFixed(1)}%
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={metrics.anomaly_detection_accuracy * 100}
                    color="success"
                    sx={{ mt: 1 }}
                  />
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Dashboard;
