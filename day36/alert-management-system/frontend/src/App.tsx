import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Dashboard from './pages/Dashboard';
import AlertRules from './pages/AlertRules';
import AlertInstances from './pages/AlertInstances';
import Navigation from './components/Navigation';

// Add CSS for rotating animation
const style = document.createElement('style');
style.textContent = `
  .rotating {
    animation: rotate 1s linear infinite;
  }
  
  @keyframes rotate {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }
`;
document.head.appendChild(style);

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#0073aa',
    },
    secondary: {
      main: '#005177',
    },
    background: {
      default: '#f6f7f7',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <div style={{ display: 'flex', minHeight: '100vh' }}>
          <Navigation />
          <main style={{ flexGrow: 1, padding: '24px' }}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/alert-rules" element={<AlertRules />} />
              <Route path="/alert-instances" element={<AlertInstances />} />
            </Routes>
          </main>
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;
