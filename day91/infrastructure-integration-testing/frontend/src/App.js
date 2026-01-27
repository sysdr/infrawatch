import React, { useState, useEffect } from 'react';
import {
  Container,
  AppBar,
  Toolbar,
  Typography,
  Box,
  Grid,
  Paper,
  Button,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  PlayArrow,
  CheckCircle,
  Error,
  Schedule,
  Speed,
  CloudQueue,
  Assessment,
  Security
} from '@mui/icons-material';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import axios from 'axios';
import './App.css';

const API_BASE_URL = 'http://localhost:8000/api/v1';

function App() {
  const [stats, setStats] = useState(null);
  const [tests, setTests] = useState([]);
  const [resources, setResources] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [costSummary, setCostSummary] = useState(null);
  const [testDialogOpen, setTestDialogOpen] = useState(false);
  const [selectedTestType, setSelectedTestType] = useState('end_to_end');
  const [chaosEnabled, setChaosEnabled] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [statsRes, testsRes, resourcesRes, metricsRes, costRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/integration/stats`),
        axios.get(`${API_BASE_URL}/integration/tests`),
        axios.get(`${API_BASE_URL}/discovery/resources`),
        axios.get(`${API_BASE_URL}/monitoring/metrics`),
        axios.get(`${API_BASE_URL}/costs/summary`)
      ]);
      
      setStats(statsRes.data);
      setTests(testsRes.data);
      setResources(resourcesRes.data);
      setMetrics(metricsRes.data);
      setCostSummary(costRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const runIntegrationTest = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/integration/tests/run`, {
        test_type: selectedTestType,
        cloud_provider: 'aws',
        resource_count: 10,
        duration_minutes: 5,
        chaos_enabled: chaosEnabled
      });
      
      setTestDialogOpen(false);
      await fetchData();
    } catch (error) {
      console.error('Error running test:', error);
    }
    setLoading(false);
  };

  const getStatusColor = (status) => {
    switch(status) {
      case 'completed': return 'success';
      case 'running': return 'info';
      case 'failed': return 'error';
      default: return 'default';
    }
  };

  const COLORS = ['#4caf50', '#2196f3', '#ff9800', '#f44336', '#9c27b0'];

  return (
    <div className="App">
      <AppBar position="static" sx={{ bgcolor: '#1a1a2e' }}>
        <Toolbar>
          <Security sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Infrastructure Integration Testing Platform
          </Typography>
          <Button 
            variant="contained" 
            color="success" 
            startIcon={<PlayArrow />}
            onClick={() => setTestDialogOpen(true)}
          >
            Run Integration Test
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        {/* Stats Overview */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={3}>
            <Paper sx={{ p: 3, bgcolor: '#e8f5e9' }}>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#2e7d32' }}>
                    {stats?.total_tests || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Tests Run
                  </Typography>
                </Box>
                <Assessment sx={{ fontSize: 40, color: '#4caf50' }} />
              </Box>
            </Paper>
          </Grid>

          <Grid item xs={12} md={3}>
            <Paper sx={{ p: 3, bgcolor: '#e3f2fd' }}>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#1565c0' }}>
                    {stats?.tests_passed || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Tests Passed
                  </Typography>
                </Box>
                <CheckCircle sx={{ fontSize: 40, color: '#2196f3' }} />
              </Box>
            </Paper>
          </Grid>

          <Grid item xs={12} md={3}>
            <Paper sx={{ p: 3, bgcolor: '#fff3e0' }}>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#e65100' }}>
                    {stats?.success_rate?.toFixed(1) || 0}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Success Rate
                  </Typography>
                </Box>
                <Speed sx={{ fontSize: 40, color: '#ff9800' }} />
              </Box>
            </Paper>
          </Grid>

          <Grid item xs={12} md={3}>
            <Paper sx={{ p: 3, bgcolor: '#f3e5f5' }}>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#6a1b9a' }}>
                    {stats?.average_duration || 0}s
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Avg Duration
                  </Typography>
                </Box>
                <Schedule sx={{ fontSize: 40, color: '#9c27b0' }} />
              </Box>
            </Paper>
          </Grid>
        </Grid>

        {/* Monitoring & Cost Overview */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>Monitoring Metrics</Typography>
              {metrics && (
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Total Metrics</Typography>
                    <Typography variant="h6">{metrics.total_metrics.toLocaleString()}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Metrics/Second</Typography>
                    <Typography variant="h6">{metrics.metrics_per_second}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Active Alerts</Typography>
                    <Typography variant="h6" color="error">{metrics.active_alerts}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Latency</Typography>
                    <Typography variant="h6">{metrics.monitoring_latency_ms}ms</Typography>
                  </Grid>
                </Grid>
              )}
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>Cost Summary</Typography>
              {costSummary && (
                <>
                  <Typography variant="h4" sx={{ color: '#4caf50', mb: 2 }}>
                    ${costSummary.total_monthly_cost.toLocaleString()}
                  </Typography>
                  <ResponsiveContainer width="100%" height={200}>
                    <PieChart>
                      <Pie
                        data={Object.entries(costSummary.cost_by_service).map(([name, value]) => ({ name, value }))}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {Object.keys(costSummary.cost_by_service).map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </>
              )}
            </Paper>
          </Grid>
        </Grid>

        {/* Recent Tests */}
        <Paper sx={{ p: 3, mb: 4 }}>
          <Typography variant="h6" gutterBottom>Recent Integration Tests</Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Test ID</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Passed</TableCell>
                  <TableCell>Failed</TableCell>
                  <TableCell>Duration</TableCell>
                  <TableCell>Started At</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {tests.slice(0, 10).map((test) => (
                  <TableRow key={test.test_id || test.started_at}>
                    <TableCell>{test.test_id || 'N/A'}</TableCell>
                    <TableCell>{test.test_type || 'N/A'}</TableCell>
                    <TableCell>
                      <Chip 
                        label={test.status} 
                        color={getStatusColor(test.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{test.tests_passed || 0}</TableCell>
                    <TableCell>{test.tests_failed || 0}</TableCell>
                    <TableCell>{test.duration_seconds ? `${test.duration_seconds}s` : 'N/A'}</TableCell>
                    <TableCell>{test.started_at ? new Date(test.started_at).toLocaleTimeString() : 'N/A'}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>

        {/* Discovered Resources */}
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>Discovered Resources ({resources.length})</Typography>
          <Grid container spacing={2}>
            {resources.slice(0, 6).map((resource) => (
              <Grid item xs={12} md={4} key={resource.id}>
                <Card>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Typography variant="h6">{resource.name}</Typography>
                      <CloudQueue color="primary" />
                    </Box>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {resource.type} • {resource.region}
                    </Typography>
                    <Box mt={2}>
                      <Chip label={resource.status} size="small" color="success" sx={{ mr: 1 }} />
                      {resource.monitored && <Chip label="Monitored" size="small" color="info" sx={{ mr: 1 }} />}
                      {resource.cost_tracked && <Chip label="Cost Tracked" size="small" color="warning" />}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Paper>
      </Container>

      {/* Test Dialog */}
      <Dialog open={testDialogOpen} onClose={() => setTestDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Run Integration Test</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Test Type</InputLabel>
              <Select
                value={selectedTestType}
                label="Test Type"
                onChange={(e) => setSelectedTestType(e.target.value)}
              >
                <MenuItem value="discovery">Resource Discovery</MenuItem>
                <MenuItem value="monitoring">Monitoring Integration</MenuItem>
                <MenuItem value="cost_tracking">Cost Tracking</MenuItem>
                <MenuItem value="automation">Automation Workflow</MenuItem>
                <MenuItem value="end_to_end">End-to-End</MenuItem>
              </Select>
            </FormControl>

            <FormControlLabel
              control={
                <Switch
                  checked={chaosEnabled}
                  onChange={(e) => setChaosEnabled(e.target.checked)}
                />
              }
              label="Enable Chaos Engineering Tests"
            />

            <Alert severity="info" sx={{ mt: 2 }}>
              This will run a comprehensive integration test validating all system components.
            </Alert>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTestDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={runIntegrationTest} 
            variant="contained" 
            disabled={loading}
          >
            {loading ? 'Starting...' : 'Start Test'}
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}

export default App;
