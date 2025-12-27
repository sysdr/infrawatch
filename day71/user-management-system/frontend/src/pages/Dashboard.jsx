import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  AppBar,
  Toolbar,
  Box
} from '@mui/material';
import { Person, Timeline, Settings, ExitToApp } from '@mui/icons-material';
import useAuthStore from '../store/authStore';

export default function Dashboard() {
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const menuItems = [
    {
      title: 'My Profile',
      description: 'View and edit your profile information',
      icon: <Person sx={{ fontSize: 40 }} />,
      path: '/profile'
    },
    {
      title: 'Activity Timeline',
      description: 'View your activity history and statistics',
      icon: <Timeline sx={{ fontSize: 40 }} />,
      path: '/activity'
    },
    {
      title: 'Preferences',
      description: 'Customize your experience',
      icon: <Settings sx={{ fontSize: 40 }} />,
      path: '/preferences'
    }
  ];

  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            User Management System
          </Typography>
          <Typography variant="body1" sx={{ mr: 2 }}>
            {user?.email}
          </Typography>
          <Button color="inherit" onClick={handleLogout} startIcon={<ExitToApp />}>
            Logout
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Paper elevation={3} sx={{ p: 4, mb: 4 }}>
          <Typography variant="h4" gutterBottom>
            Welcome back!
          </Typography>
          <Typography color="text.secondary">
            Manage your profile, view activity, and customize preferences
          </Typography>
        </Paper>

        <Grid container spacing={3}>
          {menuItems.map((item) => (
            <Grid item xs={12} md={4} key={item.title}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
                    {item.icon}
                  </Box>
                  <Typography variant="h6" align="center" gutterBottom>
                    {item.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" align="center">
                    {item.description}
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button fullWidth variant="contained" onClick={() => navigate(item.path)}>
                    Open
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>
    </>
  );
}
