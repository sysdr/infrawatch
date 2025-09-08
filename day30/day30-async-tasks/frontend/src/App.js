import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Grid,
  Card,
  CardContent,
  Button,
  Box,
  Chip,
  LinearProgress,
  Alert,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import {
  Refresh,
  Settings,
  Notifications,
  Assessment,
  PlayArrow,
  Stop,
  Warning,
  CheckCircle,
  Error as ErrorIcon
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar
} from 'recharts';
import axios from 'axios';
import './App.css';

const API_BASE = 'http://localhost:8000';

function App() {
  const [dashboardStats, setDashboardStats] = useState(null);
  const [latestMetrics, setLatestMetrics] = useState(null);
  const [activeTasks, setActiveTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedMetric, setSelectedMetric] = useState('');
  const [metricHistory, setMetricHistory] = useState([]);
  const [taskDialog, setTaskDialog] = useState({ open: false, type: '', data: {} });

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [statsRes, metricsRes, tasksRes] = await Promise.all([
        axios.get(`${API_BASE}/dashboard/stats`),
        axios.get(`${API_BASE}/metrics/latest`),
        axios.get(`${API_BASE}/tasks/active`)
      ]);

      setDashboardStats(statsRes.data);
      setLatestMetrics(metricsRes.data);
      setActiveTasks(Object.values(tasksRes.data.active_tasks || {}).flat());
      setError(null);
    } catch (err) {
      setError('Failed to fetch dashboard data');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  const triggerTask = async (taskType, params = {}) => {
    try {
      let response;
      switch (taskType) {
        case 'collect_metrics':
          response = await axios.post(`${API_BASE}/metrics/collect`);
          break;
        case 'generate_report':
          response = await axios.post(`${API_BASE}/reports/generate`, null, {
            params: { report_type: params.report_type || 'dashboard' }
          });
          break;
        case 'test_notification':
          response = await axios.post(`${API_BASE}/notifications/test`, null, {
            params: { channel: params.channel || 'slack', message: params.message || 'Test notification' }
          });
          break;
        case 'maintenance':
          response = await axios.post(`${API_BASE}/maintenance/run`);
          break;
        case 'custom_metric':
          response = await axios.post(`${API_BASE}/metrics/custom`, null, {
            params: { metric_name: params.name, value: params.value, unit: params.unit || 'count' }
          });
          break;
        default:
          throw new Error('Unknown task type');
      }
      
      alert(`Task queued! Task ID: ${response.data.task_id}`);
      fetchDashboardData();
    } catch (err) {
      alert(`Failed to trigger task: ${err.message}`);
    }
  };

  const fetchMetricHistory = async (metricName) => {
    try {
      const response = await axios.get(`${API_BASE}/metrics/history/${metricName}`);
      const data = response.data.data.map(item => ({
        timestamp: new Date(item.timestamp).toLocaleTimeString(),
        value: item.value
      }));
      setMetricHistory(data);
    } catch (err) {
      console.error('Failed to fetch metric history:', err);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy': case 'normal': return 'success';
      case 'warning': return 'warning';
      case 'critical': case 'unhealthy': return 'error';
      default: return 'info';
    }
  };

  const formatValue = (value, unit) => {
    if (unit === 'percent') return `${value.toFixed(1)}%`;
    if (unit === 'bytes') return `${(value / 1024 / 1024).toFixed(1)} MB`;
    return `${value} ${unit}`;
  };

  const TaskDialog = () => (
    <Dialog open={taskDialog.open} onClose={() => setTaskDialog({ ...taskDialog, open: false })} maxWidth="sm" fullWidth>
      <DialogTitle>Trigger Task: {taskDialog.type}</DialogTitle>
      <DialogContent>
        {taskDialog.type === 'custom_metric' && (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <TextField
              label="Metric Name"
              value={taskDialog.data.name || ''}
              onChange={(e) => setTaskDialog({
                ...taskDialog,
                data: { ...taskDialog.data, name: e.target.value }
              })}
            />
            <TextField
              label="Value"
              type="number"
              value={taskDialog.data.value || ''}
              onChange={(e) => setTaskDialog({
                ...taskDialog,
                data: { ...taskDialog.data, value: parseFloat(e.target.value) }
              })}
            />
            <TextField
              label="Unit"
              value={taskDialog.data.unit || 'count'}
              onChange={(e) => setTaskDialog({
                ...taskDialog,
                data: { ...taskDialog.data, unit: e.target.value }
              })}
            />
          </Box>
        )}
        {taskDialog.type === 'test_notification' && (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <FormControl>
              <InputLabel>Channel</InputLabel>
              <Select
                value={taskDialog.data.channel || 'slack'}
                onChange={(e) => setTaskDialog({
                  ...taskDialog,
                  data: { ...taskDialog.data, channel: e.target.value }
                })}
              >
                <MenuItem value="email">Email</MenuItem>
                <MenuItem value="slack">Slack</MenuItem>
                <MenuItem value="webhook">Webhook</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Message"
              multiline
              rows={3}
              value={taskDialog.data.message || 'Test notification'}
              onChange={(e) => setTaskDialog({
                ...taskDialog,
                data: { ...taskDialog.data, message: e.target.value }
              })}
            />
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setTaskDialog({ ...taskDialog, open: false })}>Cancel</Button>
        <Button onClick={() => {
          triggerTask(taskDialog.type, taskDialog.data);
          setTaskDialog({ ...taskDialog, open: false });
        }} variant="contained">Trigger Task</Button>
      </DialogActions>
    </Dialog>
  );

  if (loading && !dashboardStats) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <LinearProgress sx={{ width: '50%' }} />
      </Box>
    );
  }

  return (
    <div className="App">
      <AppBar position="static" sx={{ backgroundColor: '#1976d2' }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            📊 Metrics Collection Dashboard
          </Typography>
          <IconButton color="inherit" onClick={fetchDashboardData}>
            <Refresh />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* System Status Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {dashboardStats?.system && Object.entries(dashboardStats.system).map(([key, value]) => (
            <Grid item xs={12} sm={6} md={4} key={key}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" justifyContent="space-between">
                    <Typography variant="h6" component="div">
                      {key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </Typography>
                    <Chip 
                      label={formatValue(value, 'percent')} 
                      color={value > 80 ? 'error' : value > 60 ? 'warning' : 'success'}
                    />
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={value} 
                    sx={{ mt: 2 }}
                    color={value > 80 ? 'error' : value > 60 ? 'warning' : 'success'}
                  />
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        {/* Statistics Overview */}
        {dashboardStats && (
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    📈 Total Records
                  </Typography>
                  <Box display="flex" justifyContent="space-around" alignItems="center">
                    <Box textAlign="center">
                      <Typography variant="h4" color="primary">
                        {dashboardStats.totals.metrics.toLocaleString()}
                      </Typography>
                      <Typography variant="body2">Metrics</Typography>
                    </Box>
                    <Box textAlign="center">
                      <Typography variant="h4" color="secondary">
                        {dashboardStats.totals.tasks.toLocaleString()}
                      </Typography>
                      <Typography variant="body2">Tasks</Typography>
                    </Box>
                    <Box textAlign="center">
                      <Typography variant="h4" color="info.main">
                        {dashboardStats.totals.notifications.toLocaleString()}
                      </Typography>
                      <Typography variant="body2">Notifications</Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    🔥 Recent Activity (Last Hour)
                  </Typography>
                  <Box display="flex" justifyContent="space-around" alignItems="center">
                    <Box textAlign="center">
                      <Typography variant="h4" color="success.main">
                        {dashboardStats.recent_activity.metrics_last_hour}
                      </Typography>
                      <Typography variant="body2">New Metrics</Typography>
                    </Box>
                    <Box textAlign="center">
                      <Typography variant="h4" color="warning.main">
                        {dashboardStats.recent_activity.tasks_last_hour}
                      </Typography>
                      <Typography variant="body2">Tasks Executed</Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {/* Quick Actions */}
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              🚀 Quick Actions
            </Typography>
            <Grid container spacing={2}>
              <Grid item>
                <Button
                  variant="contained"
                  startIcon={<PlayArrow />}
                  onClick={() => triggerTask('collect_metrics')}
                >
                  Collect Metrics
                </Button>
              </Grid>
              <Grid item>
                <Button
                  variant="contained"
                  startIcon={<Assessment />}
                  onClick={() => triggerTask('generate_report')}
                >
                  Generate Report
                </Button>
              </Grid>
              <Grid item>
                <Button
                  variant="contained"
                  startIcon={<Notifications />}
                  onClick={() => setTaskDialog({ open: true, type: 'test_notification', data: {} })}
                >
                  Test Notification
                </Button>
              </Grid>
              <Grid item>
                <Button
                  variant="contained"
                  startIcon={<Settings />}
                  onClick={() => triggerTask('maintenance')}
                >
                  Run Maintenance
                </Button>
              </Grid>
              <Grid item>
                <Button
                  variant="outlined"
                  onClick={() => setTaskDialog({ open: true, type: 'custom_metric', data: {} })}
                >
                  Add Custom Metric
                </Button>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* Latest Metrics */}
        {latestMetrics?.summary && (
          <Card sx={{ mb: 4 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📊 Latest Metrics
              </Typography>
              <Grid container spacing={3}>
                {Object.entries(latestMetrics.summary).map(([name, data]) => (
                  <Grid item xs={12} sm={6} md={4} key={name}>
                    <Paper sx={{ p: 2, cursor: 'pointer' }} onClick={() => {
                      setSelectedMetric(name);
                      fetchMetricHistory(name);
                    }}>
                      <Box display="flex" alignItems="center" justifyContent="space-between">
                        <Typography variant="subtitle1">
                          {name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </Typography>
                        <Chip
                          size="small"
                          label={data.status}
                          color={getStatusColor(data.status)}
                          icon={
                            data.status === 'critical' ? <ErrorIcon /> :
                            data.status === 'warning' ? <Warning /> : <CheckCircle />
                          }
                        />
                      </Box>
                      <Typography variant="h5" sx={{ mt: 1 }}>
                        {formatValue(data.current, data.unit)}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Updated: {new Date(data.last_updated).toLocaleTimeString()}
                      </Typography>
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        )}

        {/* Metric History Chart */}
        {metricHistory.length > 0 && (
          <Card sx={{ mb: 4 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📈 {selectedMetric.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} History
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={metricHistory}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="timestamp" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="value" stroke="#1976d2" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        )}

        {/* Active Tasks */}
        {activeTasks.length > 0 && (
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                ⚡ Active Tasks
              </Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Task ID</TableCell>
                      <TableCell>Name</TableCell>
                      <TableCell>Worker</TableCell>
                      <TableCell>Args</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {activeTasks.map((task, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Typography variant="body2" fontFamily="monospace">
                            {task.id?.substring(0, 8)}...
                          </Typography>
                        </TableCell>
                        <TableCell>{task.name}</TableCell>
                        <TableCell>{task.worker}</TableCell>
                        <TableCell>
                          <Typography variant="body2" fontFamily="monospace">
                            {JSON.stringify(task.args).substring(0, 50)}...
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        )}
      </Container>

      <TaskDialog />
    </div>
  );
}

export default App;
