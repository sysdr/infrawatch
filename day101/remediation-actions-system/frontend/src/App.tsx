import { useState } from 'react';
import { Box, Container, Typography, AppBar, Toolbar, Tabs, Tab, Paper } from '@mui/material';
import { Security as SecurityIcon } from '@mui/icons-material';
import Dashboard from './components/Dashboard';
import ActionsList from './components/ActionsList';
import ApprovalQueue from './components/ApprovalQueue';

function App() {
  const [currentTab, setCurrentTab] = useState(0);

  return (
    <Box sx={{ flexGrow: 1, bgcolor: '#f5f5f5', minHeight: '100vh' }}>
      <AppBar position="static" sx={{ bgcolor: '#1a237e' }}>
        <Toolbar>
          <SecurityIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Remediation Actions System
          </Typography>
          <Typography variant="body2" sx={{ opacity: 0.8 }}>
            Day 101: Automated Incident Response
          </Typography>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Paper sx={{ mb: 3 }}>
          <Tabs value={currentTab} onChange={(_, v) => setCurrentTab(v)} sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tab label="Dashboard" />
            <Tab label="All Actions" />
            <Tab label="Approval Queue" />
          </Tabs>
        </Paper>

        {currentTab === 0 && <Dashboard />}
        {currentTab === 1 && <ActionsList />}
        {currentTab === 2 && <ApprovalQueue />}
      </Container>
    </Box>
  );
}

export default App;
