import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box } from '@mui/material';

import Navbar from './components/common/Navbar';
import Sidebar from './components/common/Sidebar';
import ServerManagementPage from './pages/ServerManagementPage';
import ServerDetailPage from './pages/ServerDetailPage';
import { WebSocketProvider } from './hooks/useWebSocket';
import './App.css';

// WordPress-inspired theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#2271b1',  // WordPress blue
      light: '#135e96',
      dark: '#0a4b78',
    },
    secondary: {
      main: '#dcdcde',
      light: '#f0f0f1',
      dark: '#c3c4c7',
    },
    background: {
      default: '#f0f0f1',
      paper: '#ffffff',
    },
    success: {
      main: '#00a32a',
    },
    warning: {
      main: '#dba617',
    },
    error: {
      main: '#d63638',
    },
  },
  typography: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, "Helvetica Neue", sans-serif',
    h4: {
      fontWeight: 600,
      color: '#1d2327',
    },
    h6: {
      fontWeight: 600,
      color: '#1d2327',
    },
  },
  shape: {
    borderRadius: 4,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 1px 3px rgba(0,0,0,0.13)',
          border: '1px solid #dcdcde',
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <WebSocketProvider>
        <Router>
          <Box sx={{ display: 'flex', minHeight: '100vh' }}>
            <Sidebar />
            <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
              <Navbar />
              <Box component="main" sx={{ flexGrow: 1, p: 3, bgcolor: 'background.default' }}>
                <Routes>
                  <Route path="/" element={<ServerManagementPage />} />
                  <Route path="/servers" element={<ServerManagementPage />} />
                  <Route path="/servers/:serverId" element={<ServerDetailPage />} />
                </Routes>
              </Box>
            </Box>
          </Box>
        </Router>
      </WebSocketProvider>
    </ThemeProvider>
  );
}

export default App;
