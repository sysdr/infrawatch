import React, { useState, useEffect } from 'react';
import {
  ThemeProvider, createTheme, CssBaseline, Box, AppBar, Toolbar, Typography, Container, Grid, Paper,
  Card, CardContent, Button, Chip, Tab, Tabs, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField, Select, MenuItem, FormControl, InputLabel,
  Alert, LinearProgress, IconButton,
} from '@mui/material';
import {
  Cloud as CloudIcon, Dashboard as DashboardIcon, AttachMoney as MoneyIcon, Security as SecurityIcon,
  Label as LabelIcon, Timeline as TimelineIcon, Refresh as RefreshIcon, Add as AddIcon,
  CheckCircle, Warning, Error as ErrorIcon,
} from '@mui/icons-material';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import axios from 'axios';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001';
const theme = createTheme({
  palette: { primary: { main: '#232F3E' }, secondary: { main: '#FF9900' }, success: { main: '#00A756' }, warning: { main: '#FF9900' }, error: { main: '#DD3333' } },
});
const COLORS = ['#00A756', '#FF9900', '#DD3333', '#0073BB', '#8B4513'];

function App() {
  const [currentTab, setCurrentTab] = useState(0);
  const [dashboardStats, setDashboardStats] = useState(null);
  const [resources, setResources] = useState([]);
  const [costOptimizations, setCostOptimizations] = useState([]);
  const [complianceSummary, setComplianceSummary] = useState(null);
  const [tagCompliance, setTagCompliance] = useState(null);
  const [lifecycleSummary, setLifecycleSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [provisionDialogOpen, setProvisionDialogOpen] = useState(false);
  const [newResource, setNewResource] = useState({ name: '', type: 'compute', provider: 'aws', region: 'us-east-1', team: 'engineering', size: 1 });
  const [alert, setAlert] = useState(null);

  useEffect(() => { loadDashboardData(); }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [stats, resourcesList, optimizations, compliance, tags, lifecycle] = await Promise.all([
        axios.get(`${API_BASE_URL}/api/stats/dashboard`),
        axios.get(`${API_BASE_URL}/api/resources`),
        axios.get(`${API_BASE_URL}/api/cost/optimizations`),
        axios.get(`${API_BASE_URL}/api/compliance/summary`),
        axios.get(`${API_BASE_URL}/api/tags/compliance`),
        axios.get(`${API_BASE_URL}/api/lifecycle/summary`),
      ]);
      setDashboardStats(stats.data);
      setResources(resourcesList.data);
      setCostOptimizations(optimizations.data);
      setComplianceSummary(compliance.data);
      setTagCompliance(tags.data);
      setLifecycleSummary(lifecycle.data);
    } catch (e) {
      console.error('Error loading dashboard:', e);
      setAlert({ severity: 'error', message: 'Failed to load dashboard data. Is the backend running on :8000?' });
    } finally {
      setLoading(false);
    }
  };

  const handleProvisionResource = async () => {
    try {
      await axios.post(`${API_BASE_URL}/api/resources/provision`, newResource);
      setAlert({ severity: 'success', message: 'Resource provisioning initiated' });
      setProvisionDialogOpen(false);
      loadDashboardData();
    } catch (e) {
      setAlert({ severity: 'error', message: 'Failed to provision resource' });
    }
  };

  const handleRunComplianceCheck = async () => {
    try {
      await axios.post(`${API_BASE_URL}/api/compliance/check-all`);
      setAlert({ severity: 'success', message: 'Compliance checks completed' });
      loadDashboardData();
    } catch (e) {
      setAlert({ severity: 'error', message: 'Failed to run compliance checks' });
    }
  };

  const handleAutoTag = async () => {
    try {
      await axios.post(`${API_BASE_URL}/api/tags/auto-tag`);
      setAlert({ severity: 'success', message: 'Auto-tagging completed' });
      loadDashboardData();
    } catch (e) {
      setAlert({ severity: 'error', message: 'Failed to auto-tag resources' });
    }
  };

  const getStateColor = (state) => ({ active: 'success', pending: 'warning', failed: 'error', idle: 'default', deprecated: 'warning' }[state] || 'default');

  const StatCard = ({ title, value, subtitle, icon, color }) => (
    <Card sx={{ height: '100%', background: `linear-gradient(135deg, ${color}15 0%, ${color}05 100%)` }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">{title}</Typography>
            <Typography variant="h4">{value}</Typography>
            {subtitle && <Typography variant="body2" color="textSecondary">{subtitle}</Typography>}
          </Box>
          <Box sx={{ color, fontSize: 48 }}>{icon}</Box>
        </Box>
      </CardContent>
    </Card>
  );

  const stateDist = lifecycleSummary?.state_distribution || {};
  const stateChartData = Object.entries(stateDist).map(([name, value]) => ({ name, value }));
  const totalSavings = (costOptimizations || []).reduce((s, o) => s + (o.potential_savings || 0), 0);
  const tagTotal = tagCompliance?.total_resources ?? 0;
  const tagNonCompliant = tagCompliance?.non_compliant_resources ?? 0;
  const tagPct = tagTotal > 0 ? (tagNonCompliant / tagTotal) * 100 : 0;

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Toolbar>
            <CloudIcon sx={{ mr: 2 }} />
            <Typography variant="h6" sx={{ flexGrow: 1 }}>Cloud Resource Management</Typography>
            <Button color="inherit" startIcon={<AddIcon />} onClick={() => setProvisionDialogOpen(true)}>Provision Resource</Button>
            <IconButton color="inherit" onClick={loadDashboardData}><RefreshIcon /></IconButton>
          </Toolbar>
        </AppBar>
        {loading && <LinearProgress />}
        {alert && <Alert severity={alert.severity} onClose={() => setAlert(null)} sx={{ m: 2 }}>{alert.message}</Alert>}
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
          <Tabs value={currentTab} onChange={(_, v) => setCurrentTab(v)} sx={{ mb: 3 }}>
            <Tab icon={<DashboardIcon />} label="Dashboard" />
            <Tab icon={<CloudIcon />} label="Resources" />
            <Tab icon={<MoneyIcon />} label="Cost Optimization" />
            <Tab icon={<SecurityIcon />} label="Compliance" />
            <Tab icon={<LabelIcon />} label="Tagging" />
            <Tab icon={<TimelineIcon />} label="Lifecycle" />
          </Tabs>

          {currentTab === 0 && dashboardStats && (
            <Box>
              <Grid container spacing={3} sx={{ mb: 3 }}>
                <Grid item xs={12} sm={6} md={3}>
                  <StatCard title="Total Resources" value={dashboardStats.resources?.total ?? 0} subtitle={`${dashboardStats.resources?.active ?? 0} active`} icon={<CloudIcon />} color="#0073BB" />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <StatCard title="Monthly Cost" value={`$${Number(dashboardStats.costs?.total_monthly ?? 0).toFixed(2)}`} subtitle={`$${Number(dashboardStats.costs?.potential_savings ?? 0).toFixed(2)} potential savings`} icon={<MoneyIcon />} color="#FF9900" />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <StatCard title="Compliance Rate" value={`${Number(dashboardStats.compliance?.rate ?? 0).toFixed(1)}%`} subtitle={`${dashboardStats.compliance?.total_checks ?? 0} checks`} icon={<SecurityIcon />} color="#00A756" />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <StatCard title="Tag Compliance" value={`${Number(dashboardStats.tags?.compliance_rate ?? 0).toFixed(1)}%`} subtitle="Resources properly tagged" icon={<LabelIcon />} color="#8B4513" />
                </Grid>
              </Grid>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 2 }}>
                    <Typography variant="h6" gutterBottom>Resource State Distribution</Typography>
                    {stateChartData.length > 0 ? (
                      <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                          <Pie data={stateChartData} cx="50%" cy="50%" labelLine={false} label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`} outerRadius={80} dataKey="value">
                            {stateChartData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                          </Pie>
                          <Tooltip />
                        </PieChart>
                      </ResponsiveContainer>
                    ) : (
                      <Typography color="textSecondary">No resources yet. Provision a resource or run the demo.</Typography>
                    )}
                  </Paper>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 2 }}>
                    <Typography variant="h6" gutterBottom>Cost Optimization Opportunities</Typography>
                    {costOptimizations?.length > 0 ? (
                      <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={costOptimizations.slice(0, 5).map((o) => ({ name: (o.type || '').replace(/_/g, ' '), savings: o.potential_savings || 0 }))}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="name" />
                          <YAxis />
                          <Tooltip />
                          <Bar dataKey="savings" fill="#FF9900" />
                        </BarChart>
                      </ResponsiveContainer>
                    ) : (
                      <Typography color="textSecondary">No cost optimizations. Add resources and run cost analysis.</Typography>
                    )}
                  </Paper>
                </Grid>
              </Grid>
            </Box>
          )}

          {currentTab === 1 && (
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Provider</TableCell>
                    <TableCell>Region</TableCell>
                    <TableCell>State</TableCell>
                    <TableCell>Team</TableCell>
                    <TableCell align="right">Monthly Cost</TableCell>
                    <TableCell align="right">CPU %</TableCell>
                    <TableCell>Tags</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {(resources || []).map((r) => (
                    <TableRow key={r.id}>
                      <TableCell>{r.name}</TableCell>
                      <TableCell>{r.type}</TableCell>
                      <TableCell>{r.provider}</TableCell>
                      <TableCell>{r.region}</TableCell>
                      <TableCell><Chip label={r.state} color={getStateColor(r.state)} size="small" /></TableCell>
                      <TableCell>{r.team}</TableCell>
                      <TableCell align="right">${Number(r.monthly_cost ?? 0).toFixed(2)}</TableCell>
                      <TableCell align="right">{Number(r.cpu_utilization ?? 0).toFixed(1)}%</TableCell>
                      <TableCell><Chip label={`${r.tag_count ?? 0} tags`} size="small" variant="outlined" /></TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}

          {currentTab === 2 && (
            <Box>
              <Paper sx={{ p: 2, mb: 3 }}>
                <Typography variant="h6" gutterBottom>Cost Optimization Recommendations</Typography>
                <Typography variant="body2" color="textSecondary">Total potential savings: ${Number(totalSavings).toFixed(2)}/month</Typography>
              </Paper>
              <Grid container spacing={2}>
                {(costOptimizations || []).map((o) => (
                  <Grid item xs={12} key={o.id}>
                    <Card>
                      <CardContent>
                        <Box display="flex" justifyContent="space-between" alignItems="start">
                          <Box flex={1}>
                            <Typography variant="subtitle1">{(o.type || '').replace(/_/g, ' ').toUpperCase()}</Typography>
                            <Typography variant="body2" color="textSecondary" paragraph>{o.recommendation}</Typography>
                            <Box display="flex" gap={2}>
                              <Typography variant="body2">Current: ${Number(o.current_cost ?? 0).toFixed(2)}/mo</Typography>
                              <Typography variant="body2">Optimized: ${Number(o.optimized_cost ?? 0).toFixed(2)}/mo</Typography>
                              <Typography variant="body2" color="success.main" fontWeight="bold">Savings: ${Number(o.potential_savings ?? 0).toFixed(2)}/mo</Typography>
                            </Box>
                          </Box>
                          <Chip label={`${Number((o.confidence ?? 0) * 100).toFixed(0)}% confidence`} color="primary" size="small" />
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}

          {currentTab === 3 && complianceSummary && (
            <Box>
              <Paper sx={{ p: 2, mb: 3 }}>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Box>
                    <Typography variant="h6" gutterBottom>Compliance Overview</Typography>
                    <Typography variant="h3" color="success.main">{complianceSummary.compliance_rate ?? 0}%</Typography>
                    <Typography variant="body2" color="textSecondary">Compliance Rate</Typography>
                  </Box>
                  <Button variant="contained" onClick={handleRunComplianceCheck} startIcon={<SecurityIcon />}>Run Compliance Check</Button>
                </Box>
              </Paper>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={4}><Card><CardContent><Box display="flex" alignItems="center" gap={1}><CheckCircle color="success" /><Typography variant="h4">{complianceSummary.status_counts?.compliant ?? 0}</Typography></Box><Typography color="textSecondary">Compliant</Typography></CardContent></Card></Grid>
                <Grid item xs={12} sm={4}><Card><CardContent><Box display="flex" alignItems="center" gap={1}><ErrorIcon color="error" /><Typography variant="h4">{complianceSummary.status_counts?.non_compliant ?? 0}</Typography></Box><Typography color="textSecondary">Non-Compliant</Typography></CardContent></Card></Grid>
                <Grid item xs={12} sm={4}><Card><CardContent><Box display="flex" alignItems="center" gap={1}><Warning color="warning" /><Typography variant="h4">{complianceSummary.status_counts?.warning ?? 0}</Typography></Box><Typography color="textSecondary">Warnings</Typography></CardContent></Card></Grid>
              </Grid>
            </Box>
          )}

          {currentTab === 4 && tagCompliance && (
            <Box>
              <Paper sx={{ p: 2, mb: 3 }}>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Box>
                    <Typography variant="h6" gutterBottom>Tag Compliance</Typography>
                    <Typography variant="h3" color={(tagCompliance.compliance_rate ?? 0) > 80 ? 'success.main' : 'warning.main' }>{tagCompliance.compliance_rate ?? 0}%</Typography>
                    <Typography variant="body2" color="textSecondary">{tagCompliance.compliant_resources ?? 0} of {tagTotal} resources properly tagged</Typography>
                  </Box>
                  <Button variant="contained" onClick={handleAutoTag} startIcon={<LabelIcon />}>Auto-Tag Resources</Button>
                </Box>
              </Paper>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Card><CardContent>
                    <Typography variant="h6" gutterBottom>Compliant Resources</Typography>
                    <LinearProgress variant="determinate" value={tagCompliance.compliance_rate ?? 0} color="success" sx={{ height: 10, borderRadius: 5, mb: 1 }} />
                    <Typography variant="body2">{tagCompliance.compliant_resources ?? 0} resources have all mandatory tags</Typography>
                  </CardContent></Card>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Card><CardContent>
                    <Typography variant="h6" gutterBottom>Non-Compliant Resources</Typography>
                    <LinearProgress variant="determinate" value={tagPct} color="warning" sx={{ height: 10, borderRadius: 5, mb: 1 }} />
                    <Typography variant="body2">{tagNonCompliant} resources missing mandatory tags</Typography>
                  </CardContent></Card>
                </Grid>
              </Grid>
            </Box>
          )}

          {currentTab === 5 && lifecycleSummary && (
            <Box>
              <Paper sx={{ p: 2, mb: 3 }}>
                <Typography variant="h6" gutterBottom>Lifecycle Management</Typography>
                <Typography variant="body2" color="textSecondary">{lifecycleSummary.scheduled_deletions ?? 0} resources scheduled for deletion</Typography>
              </Paper>
              <Grid container spacing={2}>
                {Object.entries(lifecycleSummary.state_distribution || {}).map(([state, count]) => (
                  <Grid item xs={12} sm={6} md={3} key={state}>
                    <Card><CardContent><Typography variant="h4">{count}</Typography><Typography color="textSecondary" textTransform="capitalize">{state}</Typography></CardContent></Card>
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}
        </Container>

        <Dialog open={provisionDialogOpen} onClose={() => setProvisionDialogOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Provision New Resource</DialogTitle>
          <DialogContent>
            <Box sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
              <TextField label="Resource Name" fullWidth value={newResource.name} onChange={(e) => setNewResource({ ...newResource, name: e.target.value })} />
              <FormControl fullWidth><InputLabel>Resource Type</InputLabel><Select value={newResource.type} onChange={(e) => setNewResource({ ...newResource, type: e.target.value })}><MenuItem value="compute">Compute</MenuItem><MenuItem value="storage">Storage</MenuItem><MenuItem value="database">Database</MenuItem><MenuItem value="network">Network</MenuItem><MenuItem value="container">Container</MenuItem></Select></FormControl>
              <FormControl fullWidth><InputLabel>Provider</InputLabel><Select value={newResource.provider} onChange={(e) => setNewResource({ ...newResource, provider: e.target.value })}><MenuItem value="aws">AWS</MenuItem><MenuItem value="gcp">Google Cloud</MenuItem><MenuItem value="azure">Azure</MenuItem></Select></FormControl>
              <TextField label="Region" fullWidth value={newResource.region} onChange={(e) => setNewResource({ ...newResource, region: e.target.value })} />
              <TextField label="Team" fullWidth value={newResource.team} onChange={(e) => setNewResource({ ...newResource, team: e.target.value })} />
              <TextField label="Size" type="number" fullWidth value={newResource.size} onChange={(e) => setNewResource({ ...newResource, size: parseInt(e.target.value, 10) || 1 })} />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setProvisionDialogOpen(false)}>Cancel</Button>
            <Button onClick={handleProvisionResource} variant="contained">Provision</Button>
          </DialogActions>
        </Dialog>
      </Box>
    </ThemeProvider>
  );
}

export default App;
