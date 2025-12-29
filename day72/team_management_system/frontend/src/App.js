import React, { useState, useEffect } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Container, Box, Tabs, Tab } from '@mui/material';
import TeamCreation from './components/teams/TeamCreation';
import TeamMembers from './components/members/TeamMembers';
import TeamDashboard from './components/dashboard/TeamDashboard';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#1976d2' },
    secondary: { main: '#dc004e' },
  },
});

// Helper function to safely access localStorage
const getLocalStorage = (key, defaultValue) => {
  try {
    const item = localStorage.getItem(key);
    return item !== null ? item : defaultValue;
  } catch (error) {
    console.warn('localStorage access failed:', error);
    return defaultValue;
  }
};

const setLocalStorage = (key, value) => {
  try {
    if (value !== null && value !== undefined) {
      localStorage.setItem(key, value.toString());
    } else {
      localStorage.removeItem(key);
    }
  } catch (error) {
    console.warn('localStorage write failed:', error);
  }
};

function App() {
  // Load state from localStorage on mount
  const [currentTab, setCurrentTab] = useState(() => {
    const saved = getLocalStorage('currentTab', '0');
    return parseInt(saved, 10) || 0;
  });
  
  const [selectedTeamId, setSelectedTeamId] = useState(() => {
    const saved = getLocalStorage('selectedTeamId', null);
    return saved ? parseInt(saved, 10) : null;
  });

  // Save state to localStorage whenever it changes
  useEffect(() => {
    setLocalStorage('currentTab', currentTab);
  }, [currentTab]);

  useEffect(() => {
    setLocalStorage('selectedTeamId', selectedTeamId);
  }, [selectedTeamId]);

  const handleTabChange = (e, newValue) => {
    setCurrentTab(newValue);
  };

  const handleTeamCreated = (teamId) => {
    setSelectedTeamId(teamId);
    // Auto-switch to Members tab when team is created
    if (teamId) {
      setCurrentTab(1);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="xl">
        <Box sx={{ borderBottom: 1, borderColor: 'divider', my: 2 }}>
          <Tabs value={currentTab} onChange={handleTabChange}>
            <Tab label="Teams" />
            <Tab label="Members" disabled={!selectedTeamId} />
            <Tab label="Dashboard" disabled={!selectedTeamId} />
          </Tabs>
        </Box>
        
        {currentTab === 0 && <TeamCreation onTeamCreated={handleTeamCreated} />}
        {currentTab === 1 && selectedTeamId && <TeamMembers teamId={selectedTeamId} />}
        {currentTab === 2 && selectedTeamId && <TeamDashboard teamId={selectedTeamId} />}
      </Container>
    </ThemeProvider>
  );
}

export default App;
