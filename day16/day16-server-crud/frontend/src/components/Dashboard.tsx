import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  AppBar,
  Toolbar,
  Container,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { serverApi, Server } from '../services/api';
import ServerIcon from '@mui/icons-material/Storage';
import AddIcon from '@mui/icons-material/Add';
import HealthIcon from '@mui/icons-material/HealthAndSafety';

const Dashboard: React.FC = () => {
  const [servers, setServers] = useState<Server[]>([]);
  const [stats, setStats] = useState({
    total: 0,
    active: 0,
    maintenance: 0,
    decommissioned: 0,
  });
  const navigate = useNavigate();

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await serverApi.list({ limit: 1000 });
      setServers(response.servers);
      
      const stats = response.servers.reduce(
        (acc, server) => {
          acc.total++;
          acc[server.status as keyof typeof acc]++;
          return acc;
        },
        { total: 0, active: 0, maintenance: 0, decommissioned: 0 }
      );
      setStats(stats);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    }
  };

  return (
    <Box sx={{ flexGrow: 1, bgcolor: '#f8f9fa', minHeight: '100vh' }}>
      <AppBar position="static" sx={{ bgcolor: '#1976d2' }}>
        <Toolbar>
          <ServerIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Server Management Dashboard
          </Typography>
          <Button
            color="inherit"
            startIcon={<AddIcon />}
            onClick={() => navigate('/servers')}
          >
            Manage Servers
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Grid container spacing={3}>
          {/* Stats Cards */}
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: '#e3f2fd' }}>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Total Servers
                </Typography>
                <Typography variant="h4" component="div">
                  {stats.total}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: '#e8f5e8' }}>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Active Servers
                </Typography>
                <Typography variant="h4" component="div" color="success.main">
                  {stats.active}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: '#fff3e0' }}>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Maintenance
                </Typography>
                <Typography variant="h4" component="div" color="warning.main">
                  {stats.maintenance}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: '#ffebee' }}>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Decommissioned
                </Typography>
                <Typography variant="h4" component="div" color="error.main">
                  {stats.decommissioned}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Quick Actions */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Quick Actions
                </Typography>
                <Grid container spacing={2}>
                  <Grid item>
                    <Button
                      variant="contained"
                      startIcon={<AddIcon />}
                      onClick={() => navigate('/servers')}
                    >
                      Add New Server
                    </Button>
                  </Grid>
                  <Grid item>
                    <Button
                      variant="outlined"
                      startIcon={<HealthIcon />}
                      onClick={() => navigate('/servers')}
                    >
                      Health Check
                    </Button>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Recent Servers */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent Servers
                </Typography>
                {servers.slice(0, 5).map((server) => (
                  <Box
                    key={server.id}
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      py: 1,
                      borderBottom: '1px solid #eee',
                    }}
                  >
                    <Box>
                      <Typography variant="subtitle1">{server.name}</Typography>
                      <Typography variant="body2" color="textSecondary">
                        {server.hostname} • {server.ip_address}
                      </Typography>
                    </Box>
                    <Typography
                      variant="body2"
                      sx={{
                        color: server.status === 'active' ? 'success.main' :
                               server.status === 'maintenance' ? 'warning.main' : 'error.main',
                        fontWeight: 'bold',
                      }}
                    >
                      {server.status.toUpperCase()}
                    </Typography>
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default Dashboard;
