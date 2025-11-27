import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box, AppBar, Toolbar, Typography, Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Container } from '@mui/material';
import { Description, Schedule, Assessment, Dashboard as DashboardIcon } from '@mui/icons-material';
import Dashboard from './pages/Dashboard';
import Templates from './pages/Templates';
import Schedules from './pages/Schedules';
import Executions from './pages/Executions';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#1976d2' },
    secondary: { main: '#dc004e' },
  },
});

const drawerWidth = 240;

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: <DashboardIcon /> },
    { id: 'templates', label: 'Templates', icon: <Description /> },
    { id: 'schedules', label: 'Schedules', icon: <Schedule /> },
    { id: 'executions', label: 'Executions', icon: <Assessment /> },
  ];

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard': return <Dashboard />;
      case 'templates': return <Templates />;
      case 'schedules': return <Schedules />;
      case 'executions': return <Executions />;
      default: return <Dashboard />;
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex' }}>
        <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
          <Toolbar>
            <Typography variant="h6" noWrap component="div">
              Report Templates System
            </Typography>
          </Toolbar>
        </AppBar>
        <Drawer
          variant="permanent"
          sx={{
            width: drawerWidth,
            flexShrink: 0,
            '& .MuiDrawer-paper': { width: drawerWidth, boxSizing: 'border-box' },
          }}
        >
          <Toolbar />
          <Box sx={{ overflow: 'auto', mt: 2 }}>
            <List>
              {menuItems.map((item) => (
                <ListItem key={item.id} disablePadding>
                  <ListItemButton
                    selected={currentPage === item.id}
                    onClick={() => setCurrentPage(item.id)}
                  >
                    <ListItemIcon>{item.icon}</ListItemIcon>
                    <ListItemText primary={item.label} />
                  </ListItemButton>
                </ListItem>
              ))}
            </List>
          </Box>
        </Drawer>
        <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
          <Toolbar />
          <Container maxWidth="xl">
            {renderPage()}
          </Container>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;
