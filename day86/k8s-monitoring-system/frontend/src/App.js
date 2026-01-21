import React, { useState, useEffect } from 'react';
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  Box,
  AppBar,
  Toolbar,
  Typography,
  Container,
  Grid,
  Tab,
  Tabs
} from '@mui/material';
import Dashboard from './components/Dashboard/Dashboard';
import PodsView from './components/Pods/PodsView';
import ServicesView from './components/Services/ServicesView';
import DeploymentsView from './components/Deployments/DeploymentsView';
import NodesView from './components/Nodes/NodesView';
import HealthView from './components/Health/HealthView';
import { useWebSocket } from './hooks/useWebSocket';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#326ce5',
    },
    secondary: {
      main: '#00c853',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

function TabPanel({ children, value, index }) {
  return (
    <div hidden={value !== index} style={{ paddingTop: '24px' }}>
      {value === index && <Box>{children}</Box>}
    </div>
  );
}

function App() {
  const [tabValue, setTabValue] = useState(0);
  const wsData = useWebSocket('ws://localhost:8000/ws/updates');

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Kubernetes Monitoring System
            </Typography>
            <Typography variant="body2">
              Cluster: Local Development
            </Typography>
          </Toolbar>
        </AppBar>

        <Container maxWidth="xl" sx={{ mt: 3 }}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={tabValue} onChange={handleTabChange}>
              <Tab label="Dashboard" />
              <Tab label="Pods" />
              <Tab label="Services" />
              <Tab label="Deployments" />
              <Tab label="Nodes" />
              <Tab label="Health" />
            </Tabs>
          </Box>

          <TabPanel value={tabValue} index={0}>
            <Dashboard wsData={wsData} />
          </TabPanel>
          <TabPanel value={tabValue} index={1}>
            <PodsView wsData={wsData} />
          </TabPanel>
          <TabPanel value={tabValue} index={2}>
            <ServicesView wsData={wsData} />
          </TabPanel>
          <TabPanel value={tabValue} index={3}>
            <DeploymentsView wsData={wsData} />
          </TabPanel>
          <TabPanel value={tabValue} index={4}>
            <NodesView wsData={wsData} />
          </TabPanel>
          <TabPanel value={tabValue} index={5}>
            <HealthView wsData={wsData} />
          </TabPanel>
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;
