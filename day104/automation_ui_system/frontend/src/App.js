import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Box, AppBar, Toolbar, Typography, Drawer, List, ListItemButton, ListItemIcon, ListItemText, CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import CodeIcon from '@mui/icons-material/Code';
import MonitorIcon from '@mui/icons-material/Monitor';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Dashboard from './components/Dashboard/Dashboard';
import WorkflowBuilder from './components/WorkflowBuilder/WorkflowBuilder';
import ScriptManager from './components/ScriptManager/ScriptManager';
import ExecutionMonitor from './components/ExecutionMonitor/ExecutionMonitor';

const drawerWidth = 240;
const theme = createTheme({ palette: { primary: { main: '#1976d2' }, secondary: { main: '#dc004e' } } });
const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { text: 'Workflow Builder', icon: <AccountTreeIcon />, path: '/workflows' },
  { text: 'Script Manager', icon: <CodeIcon />, path: '/scripts' },
  { text: 'Execution Monitor', icon: <MonitorIcon />, path: '/monitor' },
];

function App() {
  return (
    <ThemeProvider theme={theme}>
      <Router>
        <Box sx={{ display: 'flex' }}>
          <CssBaseline />
          <AppBar position="fixed" sx={{ zIndex: (t) => t.zIndex.drawer + 1 }}>
            <Toolbar><Typography variant="h6" noWrap component="div">Automation UI System</Typography></Toolbar>
          </AppBar>
          <Drawer variant="permanent" sx={{ width: drawerWidth, flexShrink: 0, ['& .MuiDrawer-paper']: { width: drawerWidth, boxSizing: 'border-box' } }}>
            <Toolbar />
            <List>
              {menuItems.map((item) => (
                <ListItemButton key={item.text} component={Link} to={item.path}>
                  <ListItemIcon>{item.icon}</ListItemIcon>
                  <ListItemText primary={item.text} />
                </ListItemButton>
              ))}
            </List>
          </Drawer>
          <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
            <Toolbar />
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/workflows" element={<WorkflowBuilder />} />
              <Route path="/scripts" element={<ScriptManager />} />
              <Route path="/monitor" element={<ExecutionMonitor />} />
            </Routes>
          </Box>
        </Box>
        <ToastContainer position="bottom-right" />
      </Router>
    </ThemeProvider>
  );
}

export default App;
