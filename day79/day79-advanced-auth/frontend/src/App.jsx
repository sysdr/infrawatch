import React, { useState } from 'react';
import {
  Container,
  Box,
  Tabs,
  Tab,
  ThemeProvider,
  createTheme,
  CssBaseline
} from '@mui/material';
import MFASetup from './components/MFASetup';
import DeviceManagement from './components/DeviceManagement';
import RiskDashboard from './components/RiskDashboard';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  const [activeTab, setActiveTab] = useState(0);
  // Get user_id from URL params or use default demo user
  const urlParams = new URLSearchParams(window.location.search);
  const userId = urlParams.get('user_id') || '23926f9a-59c0-4705-aa8e-833fc9293fa5'; // Default to demo user

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="lg">
        <Box sx={{ my: 4 }}>
          <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)} centered>
            <Tab label="MFA Setup" />
            <Tab label="Device Management" />
            <Tab label="Risk Dashboard" />
          </Tabs>

          <Box sx={{ mt: 3 }}>
            {activeTab === 0 && <MFASetup userId={userId} />}
            {activeTab === 1 && <DeviceManagement userId={userId} />}
            {activeTab === 2 && <RiskDashboard userId={userId} />}
          </Box>
        </Box>
      </Container>
    </ThemeProvider>
  );
}

export default App;
