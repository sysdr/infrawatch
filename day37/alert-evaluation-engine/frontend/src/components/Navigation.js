import React from 'react';
import { Box, Tabs, Tab } from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import DashboardIcon from '@mui/icons-material/Dashboard';
import RuleIcon from '@mui/icons-material/Rule';
import NotificationsIcon from '@mui/icons-material/Notifications';

function Navigation() {
  const navigate = useNavigate();
  const location = useLocation();
  
  const currentTab = location.pathname === '/' ? 0 : 
                    location.pathname === '/rules' ? 1 : 2;

  const handleChange = (event, newValue) => {
    const paths = ['/', '/rules', '/alerts'];
    navigate(paths[newValue]);
  };

  return (
    <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
      <Tabs value={currentTab} onChange={handleChange}>
        <Tab icon={<DashboardIcon />} label="Dashboard" />
        <Tab icon={<RuleIcon />} label="Rules" />
        <Tab icon={<NotificationsIcon />} label="Active Alerts" />
      </Tabs>
    </Box>
  );
}

export default Navigation;
