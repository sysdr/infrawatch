import React, { useState, useEffect } from 'react';
import {
  Paper, Typography, Box, Button, TextField, MenuItem, Alert,
  Card, CardContent, CardActions, Grid, Stepper, Step, StepLabel
} from '@mui/material';
import axios from 'axios';

const LIFECYCLE_STEPS = ['Pending', 'Active', 'Suspended', 'Deprovisioned'];

function Lifecycle() {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState('');
  const [targetStatus, setTargetStatus] = useState('');
  const [reason, setReason] = useState('');
  const [result, setResult] = useState(null);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/v1/users');
      setUsers(response.data);
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const handleTransition = async () => {
    if (!selectedUser || !targetStatus) return;

    try {
      const response = await axios.post(
        `http://localhost:8000/api/v1/users/${selectedUser}/lifecycle/transition?new_status=${targetStatus}&reason=${reason}`
      );
      setResult({ type: 'success', data: response.data });
      fetchUsers();
      setSelectedUser('');
      setTargetStatus('');
      setReason('');
    } catch (error) {
      setResult({ type: 'error', message: error.response?.data?.detail || error.message });
    }
  };

  const handleOffboard = async (userId) => {
    try {
      const response = await axios.post(`http://localhost:8000/api/v1/users/${userId}/lifecycle/offboard`);
      setResult({ type: 'success', data: response.data });
      fetchUsers();
    } catch (error) {
      setResult({ type: 'error', message: error.message });
    }
  };

  const getActiveStep = (status) => {
    const statusMap = { 'pending': 0, 'active': 1, 'suspended': 2, 'deprovisioned': 3 };
    return statusMap[status] || 0;
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>User Lifecycle Management</Typography>

      {result && (
        <Alert severity={result.type} sx={{ mb: 3 }} onClose={() => setResult(null)}>
          {result.message || JSON.stringify(result.data, null, 2)}
        </Alert>
      )}

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>Manual State Transition</Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={4}>
            <TextField
              select
              fullWidth
              label="Select User"
              value={selectedUser}
              onChange={(e) => setSelectedUser(e.target.value)}
            >
              {users.map((user) => (
                <MenuItem key={user.id} value={user.id}>
                  {user.username} ({user.status})
                </MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={12} sm={3}>
            <TextField
              select
              fullWidth
              label="Target Status"
              value={targetStatus}
              onChange={(e) => setTargetStatus(e.target.value)}
            >
              <MenuItem value="active">Active</MenuItem>
              <MenuItem value="suspended">Suspended</MenuItem>
              <MenuItem value="deprovisioned">Deprovisioned</MenuItem>
            </TextField>
          </Grid>
          <Grid item xs={12} sm={3}>
            <TextField
              fullWidth
              label="Reason"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
            />
          </Grid>
          <Grid item xs={12} sm={2}>
            <Button
              fullWidth
              variant="contained"
              onClick={handleTransition}
              disabled={!selectedUser || !targetStatus}
              sx={{ height: '100%' }}
            >
              Transition
            </Button>
          </Grid>
        </Grid>
      </Paper>

      <Typography variant="h6" gutterBottom>User Lifecycle Status</Typography>
      <Grid container spacing={2}>
        {users.slice(0, 6).map((user) => (
          <Grid item xs={12} md={6} key={user.id}>
            <Card>
              <CardContent>
                <Typography variant="h6">{user.username}</Typography>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  {user.email}
                </Typography>
                <Stepper activeStep={getActiveStep(user.status)} sx={{ mt: 2 }}>
                  {LIFECYCLE_STEPS.map((label) => (
                    <Step key={label}>
                      <StepLabel>{label}</StepLabel>
                    </Step>
                  ))}
                </Stepper>
                <Typography variant="body2" sx={{ mt: 2 }}>
                  Current Status: <strong>{user.status}</strong>
                </Typography>
              </CardContent>
              <CardActions>
                {user.status === 'active' && (
                  <Button size="small" color="error" onClick={() => handleOffboard(user.id)}>
                    Start Offboarding
                  </Button>
                )}
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}

export default Lifecycle;
