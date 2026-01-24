import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { Box, AppBar, Toolbar, Typography, Button, Container } from '@mui/material';
import { Dashboard, Cloud, AttachMoney, Description } from '@mui/icons-material';
import TopologyView from './components/TopologyView';
import ResourcePanel from './components/ResourcePanel';
import CostDashboard from './components/CostDashboard';
import ReportsView from './components/ReportsView';
import websocketService from './services/websocket';

function App() {
  useEffect(() => {
    // Use a stable client ID to prevent reconnection issues in React StrictMode
    const clientId = `client-${Date.now()}`;
    let mounted = true;
    
    // Small delay to ensure component is fully mounted
    const connectTimeout = setTimeout(() => {
      if (mounted) {
        websocketService.connect(clientId);
      }
    }, 100);
    
    return () => {
      mounted = false;
      clearTimeout(connectTimeout);
      // Only disconnect if we actually connected
      if (websocketService.socket && websocketService.socket.readyState !== WebSocket.CLOSED) {
        websocketService.disconnect();
      }
    };
  }, []);

  return (
    <BrowserRouter
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true,
      }}
    >
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static" sx={{ backgroundColor: '#1976d2' }}>
          <Toolbar>
            <Dashboard sx={{ mr: 2 }} />
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Infrastructure Dashboard
            </Typography>
            <Button color="inherit" component={Link} to="/" startIcon={<Cloud />}>
              Topology
            </Button>
            <Button color="inherit" component={Link} to="/resources" startIcon={<Dashboard />}>
              Resources
            </Button>
            <Button color="inherit" component={Link} to="/costs" startIcon={<AttachMoney />}>
              Costs
            </Button>
            <Button color="inherit" component={Link} to="/reports" startIcon={<Description />}>
              Reports
            </Button>
          </Toolbar>
        </AppBar>

        <Container maxWidth={false} sx={{ mt: 3 }}>
          <Routes>
            <Route path="/" element={<TopologyView />} />
            <Route path="/resources" element={<ResourcePanel />} />
            <Route path="/costs" element={<CostDashboard />} />
            <Route path="/reports" element={<ReportsView />} />
          </Routes>
        </Container>
      </Box>
    </BrowserRouter>
  );
}

export default App;
