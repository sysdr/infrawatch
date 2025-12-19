import React, { useState, useEffect } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';

import DashboardGrid from './components/dashboard/DashboardGrid';
import PerformanceMonitor from './components/performance/PerformanceMonitor';
import CacheStats from './components/performance/CacheStats';
import { useWebSocket } from './hooks/useWebSocket';
import { initDB } from './services/indexedDBService';

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
      default: '#f5f7fa',
      paper: '#ffffff',
    },
  },
});

function App() {
  const [widgetCount, setWidgetCount] = useState(50);
  const { connected, metrics } = useWebSocket('ws://localhost:8000/ws/metrics');

  useEffect(() => {
    initDB();
  }, []);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <AppBar position="static" elevation={1}>
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              High-Performance Dashboard
            </Typography>
            <Typography variant="body2" sx={{ mr: 2 }}>
              {connected ? '🟢 Connected' : '🔴 Disconnected'}
            </Typography>
            <Typography variant="body2">
              {widgetCount} Widgets
            </Typography>
          </Toolbar>
        </AppBar>

        <Container maxWidth="xl" sx={{ mt: 3, mb: 3, flexGrow: 1 }}>
          <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: 2, mb: 2 }}>
            <PerformanceMonitor />
            <CacheStats />
          </Box>
          
          <DashboardGrid 
            widgetCount={widgetCount} 
            realtimeMetrics={metrics}
          />
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;
