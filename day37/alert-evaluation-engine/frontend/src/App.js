import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Container, AppBar, Toolbar, Typography, Box } from '@mui/material';
import Dashboard from './components/Dashboard';
import RulesManager from './components/RulesManager';
import AlertsView from './components/AlertsView';
import Navigation from './components/Navigation';

// WordPress-inspired theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#0073aa', // WordPress blue
    },
    secondary: {
      main: '#00a0d2',
    },
    background: {
      default: '#f1f1f1',
    },
  },
  typography: {
    fontFamily: '"Open Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          boxShadow: '0 1px 3px rgba(0,0,0,0.13)',
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              🚨 Alert Evaluation Engine
            </Typography>
          </Toolbar>
        </AppBar>
        <Container maxWidth="xl" sx={{ mt: 3 }}>
          <Navigation />
          <Box sx={{ mt: 3 }}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/rules" element={<RulesManager />} />
              <Route path="/alerts" element={<AlertsView />} />
            </Routes>
          </Box>
        </Container>
      </Router>
    </ThemeProvider>
  );
}

export default App;
