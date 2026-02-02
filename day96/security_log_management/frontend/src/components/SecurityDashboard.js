import React, { useState, useEffect } from 'react';
import { Grid, Paper, Typography, Box, Chip, Card, CardContent } from '@mui/material';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { securityApi } from '../services/api';
import SecurityIcon from '@mui/icons-material/Security';
import WarningIcon from '@mui/icons-material/Warning';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';

const COLORS = ['#4caf50', '#ff9800', '#f44336', '#2196f3'];

function SecurityDashboard() {
  const [stats, setStats] = useState(null);
  const [recentEvents, setRecentEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      const [statsRes, eventsRes] = await Promise.all([
        securityApi.getStats(),
        securityApi.getEvents({ limit: 10 })
      ]);
      
      setStats(statsRes.data);
      setRecentEvents(eventsRes.data.events || []);
      setLoading(false);
    } catch (error) {
      console.error('Error loading dashboard:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return <Typography>Loading security dashboard...</Typography>;
  }

  const eventTypeData = stats?.events_by_type ? 
    Object.entries(stats.events_by_type).map(([name, value]) => ({ name, value })) : [];

  const severityData = [
    { name: 'Low', value: recentEvents.filter(e => e.severity === 'low').length },
    { name: 'Medium', value: recentEvents.filter(e => e.severity === 'medium').length },
    { name: 'High', value: recentEvents.filter(e => e.severity === 'high').length },
    { name: 'Critical', value: recentEvents.filter(e => e.severity === 'critical').length },
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Security Dashboard
      </Typography>

      {/* Metric Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Events (24h)
                  </Typography>
                  <Typography variant="h4">
                    {stats?.events_last_24h || 0}
                  </Typography>
                </Box>
                <SecurityIcon sx={{ fontSize: 48, color: '#2196f3', opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    High Severity
                  </Typography>
                  <Typography variant="h4" color="error">
                    {stats?.high_severity_events || 0}
                  </Typography>
                </Box>
                <ErrorIcon sx={{ fontSize: 48, color: '#f44336', opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Threats Detected
                  </Typography>
                  <Typography variant="h4" color="warning.main">
                    {stats?.threats_detected || 0}
                  </Typography>
                </Box>
                <WarningIcon sx={{ fontSize: 48, color: '#ff9800', opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Events
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {stats?.total_events || 0}
                  </Typography>
                </Box>
                <CheckCircleIcon sx={{ fontSize: 48, color: '#4caf50', opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Events by Type
            </Typography>
            <ResponsiveContainer width="100%" height="90%">
              <BarChart data={eventTypeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#2196f3" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Severity Distribution
            </Typography>
            <ResponsiveContainer width="100%" height="90%">
              <PieChart>
                <Pie
                  data={severityData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {severityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Recent Events */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Recent Security Events
            </Typography>
            {recentEvents.map((event, idx) => (
              <Box
                key={idx}
                sx={{
                  p: 2,
                  mb: 1,
                  border: '1px solid #e0e0e0',
                  borderRadius: 1,
                  backgroundColor: event.threat_indicators ? '#fff3e0' : '#fff',
                }}
              >
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Box>
                    <Typography variant="body1">
                      <strong>{event.event_type}</strong> - {event.action || 'N/A'}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      User: {event.username || event.user_id || 'Unknown'} | 
                      IP: {event.ip_address} | 
                      Time: {new Date(event.timestamp).toLocaleString()}
                    </Typography>
                  </Box>
                  <Box>
                    <Chip
                      label={event.severity}
                      color={
                        event.severity === 'critical' ? 'error' :
                        event.severity === 'high' ? 'warning' :
                        event.severity === 'medium' ? 'info' : 'default'
                      }
                      size="small"
                      sx={{ mr: 1 }}
                    />
                    <Chip
                      label={event.result}
                      color={event.result === 'success' ? 'success' : 'default'}
                      size="small"
                    />
                  </Box>
                </Box>
                {event.threat_indicators && (
                  <Box mt={1}>
                    <Chip
                      icon={<WarningIcon />}
                      label="Threat Detected"
                      color="warning"
                      size="small"
                    />
                  </Box>
                )}
              </Box>
            ))}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default SecurityDashboard;
