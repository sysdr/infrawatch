import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box, AppBar, Toolbar, Typography, Tabs, Tab, Container } from '@mui/material';
import Dashboard from './components/Dashboard/Dashboard';
import ReportBuilder from './components/ReportBuilder/ReportBuilder';
import TemplateManager from './components/TemplateManager/TemplateManager';
import ScheduleManager from './components/ScheduleManager/ScheduleManager';
import DistributionManager from './components/DistributionManager/DistributionManager';
import AssessmentIcon from '@mui/icons-material/Assessment';

const theme = createTheme({
  palette: {
    primary: {
      main: '#2C3E50',
    },
    secondary: {
      main: '#3498DB',
    },
    background: {
      default: '#ECF0F1',
    },
  },
});

function TabPanel({ children, value, index }) {
  return (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

function App() {
  const [activeTab, setActiveTab] = useState(0);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static" elevation={2}>
          <Toolbar>
            <AssessmentIcon sx={{ mr: 2, fontSize: 32 }} />
            <Typography variant="h5" component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
              Advanced Reporting System
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.8 }}>
              Day 110: Production-Grade Reporting Infrastructure
            </Typography>
          </Toolbar>
        </AppBar>
        
        <Container maxWidth="xl" sx={{ mt: 3 }}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider', bgcolor: 'white', borderRadius: 1 }}>
            <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)}>
              <Tab label="Dashboard" />
              <Tab label="Report Builder" />
              <Tab label="Templates" />
              <Tab label="Schedules" />
              <Tab label="Distribution" />
            </Tabs>
          </Box>
          
          <TabPanel value={activeTab} index={0}>
            <Dashboard />
          </TabPanel>
          <TabPanel value={activeTab} index={1}>
            <ReportBuilder />
          </TabPanel>
          <TabPanel value={activeTab} index={2}>
            <TemplateManager />
          </TabPanel>
          <TabPanel value={activeTab} index={3}>
            <ScheduleManager />
          </TabPanel>
          <TabPanel value={activeTab} index={4}>
            <DistributionManager />
          </TabPanel>
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;
