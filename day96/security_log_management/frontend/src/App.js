import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Container, AppBar, Toolbar, Typography, Tabs, Tab, Box } from '@mui/material';
import SecurityDashboard from './components/SecurityDashboard';
import AuditTrail from './components/AuditTrail';
import IncidentManagement from './components/IncidentManagement';
import ComplianceReports from './components/ComplianceReports';

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
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

function App() {
  const [activeTab, setActiveTab] = useState(0);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Security Log Management System
          </Typography>
        </Toolbar>
      </AppBar>
      
      <Container maxWidth="xl" sx={{ mt: 3 }}>
        <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)} sx={{ mb: 2 }}>
          <Tab label="Security Dashboard" />
          <Tab label="Audit Trail" />
          <Tab label="Incidents" />
          <Tab label="Compliance" />
        </Tabs>

        <TabPanel value={activeTab} index={0}>
          <SecurityDashboard />
        </TabPanel>
        <TabPanel value={activeTab} index={1}>
          <AuditTrail />
        </TabPanel>
        <TabPanel value={activeTab} index={2}>
          <IncidentManagement />
        </TabPanel>
        <TabPanel value={activeTab} index={3}>
          <ComplianceReports />
        </TabPanel>
      </Container>
    </ThemeProvider>
  );
}

export default App;
