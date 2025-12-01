import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Box, Container, AppBar, Toolbar, Typography, Tabs, Tab } from '@mui/material';
import ChartDashboard from './components/ChartDashboard';
import TrendAnalysis from './components/TrendAnalysis';
import DrillDownExplorer from './components/DrillDownExplorer';
import ComparisonTool from './components/ComparisonTool';

const queryClient = new QueryClient();

function App() {
  const [activeTab, setActiveTab] = useState(0);

  return (
    <QueryClientProvider client={queryClient}>
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static" sx={{ backgroundColor: '#1976d2' }}>
          <Toolbar>
            <Typography variant="h5" component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
              📊 Notification Analytics Dashboard
            </Typography>
          </Toolbar>
        </AppBar>
        
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
            <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)}>
              <Tab label="Charts" />
              <Tab label="Trends" />
              <Tab label="Comparison" />
              <Tab label="Drill-Down" />
            </Tabs>
          </Box>
          
          {activeTab === 0 && <ChartDashboard />}
          {activeTab === 1 && <TrendAnalysis />}
          {activeTab === 2 && <ComparisonTool />}
          {activeTab === 3 && <DrillDownExplorer />}
        </Container>
      </Box>
    </QueryClientProvider>
  );
}

export default App;
