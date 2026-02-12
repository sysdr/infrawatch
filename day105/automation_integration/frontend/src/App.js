import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';

import ExecutionDashboard from './components/Dashboard/ExecutionDashboard';
import WorkflowExecution from './components/WorkflowExecution/WorkflowExecution';
import SecurityValidation from './components/SecurityValidation/SecurityValidation';
import ErrorRecovery from './components/ErrorRecovery/ErrorRecovery';
import ExecutionMonitoring from './components/ExecutionMonitoring/ExecutionMonitoring';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
});

function TabPanel({ children, value, index }) {
  return (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

function App() {
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              🤖 Automation Integration Dashboard
            </Typography>
            <Typography variant="body2">
              Production Workflow Execution Engine
            </Typography>
          </Toolbar>
        </AppBar>

        <Container maxWidth="xl" sx={{ mt: 4, mb: 4, flexGrow: 1 }}>
          <Paper sx={{ p: 2, mb: 3 }}>
            <Tabs value={tabValue} onChange={handleTabChange}>
              <Tab label="Dashboard" />
              <Tab label="Workflow Execution" />
              <Tab label="Security Validation" />
              <Tab label="Error Recovery" />
              <Tab label="Monitoring" />
            </Tabs>
          </Paper>

          <TabPanel value={tabValue} index={0}>
            <ExecutionDashboard />
          </TabPanel>
          <TabPanel value={tabValue} index={1}>
            <WorkflowExecution />
          </TabPanel>
          <TabPanel value={tabValue} index={2}>
            <SecurityValidation />
          </TabPanel>
          <TabPanel value={tabValue} index={3}>
            <ErrorRecovery />
          </TabPanel>
          <TabPanel value={tabValue} index={4}>
            <ExecutionMonitoring />
          </TabPanel>
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;
