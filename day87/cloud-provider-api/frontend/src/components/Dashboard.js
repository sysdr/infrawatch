import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  Cloud,
  AttachMoney,
  HealthAndSafety,
  TrendingUp
} from '@mui/icons-material';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { resourcesAPI, costsAPI, healthAPI, autoscalingAPI } from '../services/api';

const COLORS = ['#48bb78', '#38b2ac', '#4299e1', '#667eea', '#f59e0b'];

function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [resources, setResources] = useState([]);
  const [resourceSummary, setResourceSummary] = useState(null);
  const [costSummary, setCostSummary] = useState(null);
  const [healthSummary, setHealthSummary] = useState(null);
  const [autoscalingEvents, setAutoscalingEvents] = useState([]);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      const [resourcesRes, resSummaryRes, costSummaryRes, healthSummaryRes, eventsRes] = await Promise.all([
        resourcesAPI.getAll(),
        resourcesAPI.getSummary(),
        costsAPI.getSummary(),
        healthAPI.getSummary(),
        autoscalingAPI.getEvents(24)
      ]);

      setResources(resourcesRes.data);
      setResourceSummary(resSummaryRes.data);
      setCostSummary(costSummaryRes.data);
      setHealthSummary(healthSummaryRes.data);
      setAutoscalingEvents(eventsRes.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch data: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    
    return () => clearInterval(interval);
  }, []);

  if (loading && !resourceSummary) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress size={60} />
      </Box>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  const resourceTypeData = resourceSummary?.by_type
    ? Object.entries(resourceSummary.by_type).map(([name, value]) => ({ name: name.toUpperCase(), value }))
    : [];

  const costByTypeData = costSummary?.by_type
    ? Object.entries(costSummary.by_type).map(([name, value]) => ({ name: name.toUpperCase(), value }))
    : [];

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom fontWeight="bold" sx={{ mb: 4 }}>
        Cloud Infrastructure Management
      </Typography>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h3" fontWeight="bold">
                    {resourceSummary?.total || 0}
                  </Typography>
                  <Typography variant="body2">Total Resources</Typography>
                </Box>
                <Cloud sx={{ fontSize: 48, opacity: 0.8 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h3" fontWeight="bold">
                    ${costSummary?.total_cost_usd?.toFixed(2) || '0.00'}
                  </Typography>
                  <Typography variant="body2">Current Cost/Day</Typography>
                </Box>
                <AttachMoney sx={{ fontSize: 48, opacity: 0.8 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h3" fontWeight="bold">
                    {healthSummary?.healthy || 0}
                  </Typography>
                  <Typography variant="body2">Healthy Resources</Typography>
                </Box>
                <HealthAndSafety sx={{ fontSize: 48, opacity: 0.8 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h3" fontWeight="bold">
                    {autoscalingEvents?.length || 0}
                  </Typography>
                  <Typography variant="body2">Scaling Events (24h)</Typography>
                </Box>
                <TrendingUp sx={{ fontSize: 48, opacity: 0.8 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts Row */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom fontWeight="bold">
              Resource Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={resourceTypeData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {resourceTypeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom fontWeight="bold">
              Cost Breakdown by Service
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={costByTypeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
                <Bar dataKey="value" fill="#48bb78" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* Health Status */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom fontWeight="bold">
              Health Status Overview
            </Typography>
            <Box display="flex" gap={2} flexWrap="wrap">
              <Chip
                label={`Healthy: ${healthSummary?.healthy || 0}`}
                sx={{ bgcolor: '#48bb78', color: 'white', fontWeight: 'bold' }}
              />
              <Chip
                label={`Degraded: ${healthSummary?.degraded || 0}`}
                sx={{ bgcolor: '#f59e0b', color: 'white', fontWeight: 'bold' }}
              />
              <Chip
                label={`Unhealthy: ${healthSummary?.unhealthy || 0}`}
                sx={{ bgcolor: '#f56565', color: 'white', fontWeight: 'bold' }}
              />
              <Chip
                label={`Unknown: ${healthSummary?.unknown || 0}`}
                sx={{ bgcolor: '#cbd5e0', color: '#2d3748', fontWeight: 'bold' }}
              />
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Resources Table */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom fontWeight="bold">
              Resource Inventory
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell><strong>Resource ID</strong></TableCell>
                    <TableCell><strong>Type</strong></TableCell>
                    <TableCell><strong>Region</strong></TableCell>
                    <TableCell><strong>Name</strong></TableCell>
                    <TableCell><strong>State</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {resources.slice(0, 10).map((resource, index) => (
                    <TableRow key={index} hover>
                      <TableCell>{resource.resource_id}</TableCell>
                      <TableCell>
                        <Chip label={resource.resource_type.toUpperCase()} size="small" color="primary" />
                      </TableCell>
                      <TableCell>{resource.region}</TableCell>
                      <TableCell>{resource.name}</TableCell>
                      <TableCell>
                        <Chip
                          label={resource.state}
                          size="small"
                          color={resource.state === 'running' || resource.state === 'available' ? 'success' : 'default'}
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* Auto-Scaling Events */}
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom fontWeight="bold">
              Recent Auto-Scaling Events
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell><strong>Group Name</strong></TableCell>
                    <TableCell><strong>Event</strong></TableCell>
                    <TableCell><strong>Trigger</strong></TableCell>
                    <TableCell><strong>Capacity Change</strong></TableCell>
                    <TableCell><strong>Cost Impact</strong></TableCell>
                    <TableCell><strong>Time</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {autoscalingEvents.slice(0, 5).map((event, index) => (
                    <TableRow key={index} hover>
                      <TableCell>{event.group_name}</TableCell>
                      <TableCell>
                        <Chip
                          label={event.event_type.replace('_', ' ').toUpperCase()}
                          size="small"
                          color={event.event_type === 'scale_up' ? 'success' : 'warning'}
                        />
                      </TableCell>
                      <TableCell>
                        {event.trigger_metric}: {event.trigger_value.toFixed(1)}%
                      </TableCell>
                      <TableCell>
                        {event.old_capacity} → {event.new_capacity}
                      </TableCell>
                      <TableCell>${event.cost_impact.toFixed(2)}</TableCell>
                      <TableCell>{new Date(event.timestamp).toLocaleString()}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
}

export default Dashboard;
