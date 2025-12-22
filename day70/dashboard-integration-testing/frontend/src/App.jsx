import React, { useEffect, useState } from 'react';
import { ThemeProvider, createTheme, CssBaseline, Box, Container } from '@mui/material';
import DashboardLayout from './components/Dashboard/DashboardLayout';
import { useWebSocket } from './hooks/useWebSocket';
import { useDashboardStore } from './store/dashboardStore';

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
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  },
});

function App() {
  const { isConnected, metrics, performanceStats } = useWebSocket();
  const updateMetrics = useDashboardStore((state) => state.updateMetrics);
  const updatePerformance = useDashboardStore((state) => state.updatePerformance);

  useEffect(() => {
    if (metrics.length > 0) {
      updateMetrics(metrics);
    }
  }, [metrics, updateMetrics]);

  useEffect(() => {
    if (performanceStats) {
      updatePerformance(performanceStats);
    }
  }, [performanceStats, updatePerformance]);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
        <Container maxWidth={false}>
          <DashboardLayout isConnected={isConnected} />
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;
