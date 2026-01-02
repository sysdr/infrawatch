import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box, AppBar, Toolbar, Typography, Container, Tabs, Tab } from '@mui/material';
import PermissionMatrix from './components/PermissionMatrix';
import AuditLog from './components/AuditLog';
import ComplianceDashboard from './components/ComplianceDashboard';
import PolicyEditor from './components/PolicyEditor';

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
  const [activeTab, setActiveTab] = useState(0);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Advanced RBAC System
            </Typography>
          </Toolbar>
        </AppBar>
        
        <Container maxWidth="xl" sx={{ mt: 4 }}>
          <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)} aria-label="rbac tabs">
            <Tab label="Permission Matrix" />
            <Tab label="Policy Editor" />
            <Tab label="Audit Log" />
            <Tab label="Compliance" />
          </Tabs>
          
          <TabPanel value={activeTab} index={0}>
            <PermissionMatrix />
          </TabPanel>
          
          <TabPanel value={activeTab} index={1}>
            <PolicyEditor />
          </TabPanel>
          
          <TabPanel value={activeTab} index={2}>
            <AuditLog />
          </TabPanel>
          
          <TabPanel value={activeTab} index={3}>
            <ComplianceDashboard />
          </TabPanel>
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;
