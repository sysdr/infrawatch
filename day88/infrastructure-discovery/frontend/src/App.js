import React, { useState, useEffect } from 'react';
import { 
  Box, Container, AppBar, Toolbar, Typography, Tabs, Tab,
  Card, CardContent, Grid, Paper
} from '@mui/material';
import DiscoveryDashboard from './components/DiscoveryDashboard';
import InventoryView from './components/InventoryView';
import TopologyGraph from './components/TopologyGraph';
import ChangesView from './components/ChangesView';
import { fetchStats } from './services/api';

function TabPanel({ children, value, index }) {
  return (
    <div hidden={value !== index} style={{ paddingTop: 20 }}>
      {value === index && children}
    </div>
  );
}

function App() {
  const [tabValue, setTabValue] = useState(0);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    loadStats();
    const interval = setInterval(loadStats, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadStats = async () => {
    const data = await fetchStats();
    setStats(data);
  };

  return (
    <Box sx={{ flexGrow: 1, bgcolor: '#f5f5f5', minHeight: '100vh' }}>
      <AppBar position="static" sx={{ bgcolor: '#1976d2' }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Infrastructure Discovery System
          </Typography>
          {stats && (
            <Typography variant="body2">
              {stats.total_resources} Resources Discovered
            </Typography>
          )}
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 3 }}>
        <Paper sx={{ borderRadius: 2, overflow: 'hidden' }}>
          <Tabs 
            value={tabValue} 
            onChange={(e, v) => setTabValue(v)}
            sx={{ borderBottom: 1, borderColor: 'divider' }}
          >
            <Tab label="Overview" />
            <Tab label="Inventory" />
            <Tab label="Topology Map" />
            <Tab label="Changes" />
          </Tabs>

          <TabPanel value={tabValue} index={0}>
            <DiscoveryDashboard stats={stats} />
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            <InventoryView />
          </TabPanel>

          <TabPanel value={tabValue} index={2}>
            <TopologyGraph />
          </TabPanel>

          <TabPanel value={tabValue} index={3}>
            <ChangesView />
          </TabPanel>
        </Paper>
      </Container>
    </Box>
  );
}

export default App;
