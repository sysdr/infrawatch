import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { Link, useLocation } from 'react-router-dom';
import TimelineIcon from '@mui/icons-material/Timeline';

const Navigation = () => {
  const location = useLocation();

  return (
    <AppBar position="static" sx={{ bgcolor: '#23282d' }}>
      <Toolbar>
        <TimelineIcon sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Metrics Dashboard
        </Typography>
        <Box>
          <Button 
            color="inherit" 
            component={Link} 
            to="/"
            sx={{ 
              color: location.pathname === '/' ? '#0073aa' : '#b4b9be',
              '&:hover': { color: '#0073aa' }
            }}
          >
            Dashboard
          </Button>
          <Button 
            color="inherit" 
            component={Link} 
            to="/metrics"
            sx={{ 
              color: location.pathname === '/metrics' ? '#0073aa' : '#b4b9be',
              '&:hover': { color: '#0073aa' }
            }}
          >
            Metrics
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navigation;
