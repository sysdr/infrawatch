import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Container, AppBar, Toolbar, Typography, Box, Tabs, Tab } from '@mui/material';
import LogStreamViewer from './components/LogStreamViewer';
import LogSearchInterface from './components/LogSearchInterface';
import SecurityAlerts from './components/SecurityAlerts';
import PerformanceMetrics from './components/PerformanceMetrics';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function TabPanel({ children, value, index }) {
  return (
    <div hidden={value !== index} style={{ padding: '24px 0' }}>
      {value === index && children}
    </div>
  );
}

function App() {
  const [currentTab, setCurrentTab] = useState(0);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Log Management Integration Dashboard
          </Typography>
          <Typography variant="body2">Day 98: Production Log Pipeline</Typography>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 3 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={currentTab} onChange={(e, newValue) => setCurrentTab(newValue)}>
            <Tab label="Real-time Stream" />
            <Tab label="Search Logs" />
            <Tab label="Security Alerts" />
            <Tab label="Performance Metrics" />
          </Tabs>
        </Box>

        <TabPanel value={currentTab} index={0}>
          <LogStreamViewer />
        </TabPanel>

        <TabPanel value={currentTab} index={1}>
          <LogSearchInterface />
        </TabPanel>

        <TabPanel value={currentTab} index={2}>
          <SecurityAlerts />
        </TabPanel>

        <TabPanel value={currentTab} index={3}>
          <PerformanceMetrics />
        </TabPanel>
      </Container>
    </ThemeProvider>
  );
}

export default App;
