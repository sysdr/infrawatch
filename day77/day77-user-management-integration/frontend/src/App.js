import React, { useState, useEffect } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box, AppBar, Toolbar, Typography, Container, Tabs, Tab } from '@mui/material';
import { Toaster } from 'react-hot-toast';
import Dashboard from './components/Dashboard/Dashboard';
import UsersPanel from './components/Users/UsersPanel';
import TeamsPanel from './components/Teams/TeamsPanel';
import TestsPanel from './components/Tests/TestsPanel';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#2e7d32',
    },
    secondary: {
      main: '#66bb6a',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
  },
});

function App() {
  const [currentTab, setCurrentTab] = useState(0);

  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Toaster position="top-right" />
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <AppBar position="static" elevation={0}>
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              User Management Integration System
            </Typography>
          </Toolbar>
        </AppBar>
        
        <Box sx={{ borderBottom: 1, borderColor: 'divider', bgcolor: 'background.paper' }}>
          <Container maxWidth="xl">
            <Tabs value={currentTab} onChange={handleTabChange}>
              <Tab label="Dashboard" />
              <Tab label="Users" />
              <Tab label="Teams" />
              <Tab label="Tests" />
            </Tabs>
          </Container>
        </Box>

        <Container maxWidth="xl" sx={{ mt: 4, mb: 4, flexGrow: 1 }}>
          {currentTab === 0 && <Dashboard />}
          {currentTab === 1 && <UsersPanel />}
          {currentTab === 2 && <TeamsPanel />}
          {currentTab === 3 && <TestsPanel />}
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;
