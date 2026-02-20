import React, { useState } from 'react';
import { Box, Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Typography, AppBar, Toolbar, Chip } from '@mui/material';
import { Dashboard as DashIcon, Psychology, Assessment, ScatterPlot, Settings } from '@mui/icons-material';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Dashboard from './components/dashboard/Dashboard';
import MLInterface from './components/ml/MLInterface';
import BIReporting from './components/reporting/BIReporting';
import CorrelationViewer from './components/correlation/CorrelationViewer';
import Configuration from './components/configuration/Configuration';

const DRAWER_W = 220;

const theme = createTheme({
  palette: { mode: 'dark', primary: { main: '#52b788' }, background: { default: '#0f1923', paper: '#1a2535' } },
  typography: { fontFamily: "'Inter', sans-serif" },
});

const NAV = [
  { label: 'Dashboard', icon: <DashIcon/>, component: <Dashboard/> },
  { label: 'ML Interface', icon: <Psychology/>, component: <MLInterface/> },
  { label: 'BI Reporting', icon: <Assessment/>, component: <BIReporting/> },
  { label: 'Correlation', icon: <ScatterPlot/>, component: <CorrelationViewer/> },
  { label: 'Configuration', icon: <Settings/>, component: <Configuration/> },
];

export default function App() {
  const [active, setActive] = useState(0);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline/>
      <Box sx={{ display: 'flex' }}>
        <Drawer variant="permanent" sx={{
          width: DRAWER_W, flexShrink: 0,
          '& .MuiDrawer-paper': { width: DRAWER_W, background: '#0d1621', border: 'none', borderRight: '1px solid #1a2535' }
        }}>
          <Box sx={{ p: 3, borderBottom: '1px solid #1a2535' }}>
            <Typography sx={{ color: '#52b788', fontWeight: 800, fontSize: 16, letterSpacing: 0.5, fontFamily: 'Inter' }}>
              ● AnalyticsPro
            </Typography>
            <Typography sx={{ color: '#556677', fontSize: 10, mt: 0.5 }}>Infrastructure Intelligence</Typography>
          </Box>
          <List sx={{ pt: 2 }}>
            {NAV.map((item, i) => (
              <ListItem key={item.label} disablePadding sx={{ mb: 0.5 }}>
                <ListItemButton onClick={() => setActive(i)}
                  sx={{ mx: 1, borderRadius: 2, py: 1,
                        background: active === i ? '#1b4332' : 'transparent',
                        '&:hover': { background: active === i ? '#1b4332' : '#162030' } }}>
                  <ListItemIcon sx={{ color: active === i ? '#52b788' : '#556677', minWidth: 36 }}>
                    {item.icon}
                  </ListItemIcon>
                  <ListItemText primary={item.label}
                    primaryTypographyProps={{ sx: { color: active === i ? '#e8f5e9' : '#8899aa', fontSize: 13, fontWeight: active === i ? 600 : 400 } }}/>
                </ListItemButton>
              </ListItem>
            ))}
          </List>
          <Box sx={{ position: 'absolute', bottom: 20, left: 0, right: 0, px: 2 }}>
            <Typography sx={{ color: '#334455', fontSize: 9, textAlign: 'center' }}>Day 111 · Week 11 · v1.0</Typography>
          </Box>
        </Drawer>

        <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
          <AppBar position="static" elevation={0} sx={{ background: '#0d1621', borderBottom: '1px solid #1a2535' }}>
            <Toolbar sx={{ justifyContent: 'space-between' }}>
              <Typography sx={{ color: '#e8f5e9', fontWeight: 600, fontSize: 15 }}>{NAV[active].label}</Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Chip label="LIVE" size="small" sx={{ background: '#1b4332', color: '#52b788', fontSize: 9,
                                                       animation: 'pulse 2s infinite',
                                                       '@keyframes pulse': { '0%,100%': { opacity: 1 }, '50%': { opacity: 0.5 } } }}/>
                <Chip label="Production" size="small" sx={{ background: '#162030', color: '#8899aa', fontSize: 9 }}/>
              </Box>
            </Toolbar>
          </AppBar>
          <Box sx={{ flexGrow: 1, p: 3, overflow: 'auto' }}>
            {NAV[active].component}
          </Box>
        </Box>
      </Box>
    </ThemeProvider>
  );
}
