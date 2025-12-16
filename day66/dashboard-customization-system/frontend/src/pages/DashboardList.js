import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Button,
  Card,
  CardContent,
  CardActions,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { dashboardApi } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const DashboardList = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [dashboards, setDashboards] = useState([]);
  const [createDialog, setCreateDialog] = useState(false);
  const [newDashboard, setNewDashboard] = useState({ name: '', description: '' });

  useEffect(() => {
    if (user) {
      loadDashboards();
    }
  }, [user]);

  const loadDashboards = async () => {
    try {
      const response = await dashboardApi.list(false);
      setDashboards(response.data);
    } catch (error) {
      console.error('Failed to load dashboards:', error);
    }
  };

  const handleCreate = async () => {
    try {
      const response = await dashboardApi.create({
        name: newDashboard.name,
        description: newDashboard.description,
        config: { layout: [], metadata: {} },
        theme: 'light'
      });
      navigate(`/dashboard/${response.data.id}`);
    } catch (error) {
      console.error('Failed to create dashboard:', error);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 4 }}>
        <Typography variant="h4">My Dashboards</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setCreateDialog(true)}
        >
          New Dashboard
        </Button>
      </Box>

      <Grid container spacing={3}>
        {dashboards.map((dashboard) => (
          <Grid item xs={12} sm={6} md={4} key={dashboard.id}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {dashboard.name}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {dashboard.description || 'No description'}
                </Typography>
                <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                  Updated: {new Date(dashboard.updated_at).toLocaleDateString()}
                </Typography>
              </CardContent>
              <CardActions>
                <Button size="small" onClick={() => navigate(`/dashboard/${dashboard.id}`)}>
                  Open
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Dialog 
        open={createDialog} 
        onClose={() => setCreateDialog(false)}
        aria-labelledby="create-dashboard-dialog-title"
      >
        <DialogTitle id="create-dashboard-dialog-title">Create New Dashboard</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Dashboard Name"
            fullWidth
            value={newDashboard.name}
            onChange={(e) => setNewDashboard({ ...newDashboard, name: e.target.value })}
          />
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            multiline
            rows={3}
            value={newDashboard.description}
            onChange={(e) => setNewDashboard({ ...newDashboard, description: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialog(false)}>Cancel</Button>
          <Button onClick={handleCreate} variant="contained">Create</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default DashboardList;
