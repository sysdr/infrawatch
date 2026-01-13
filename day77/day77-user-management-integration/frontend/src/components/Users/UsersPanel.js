import React, { useState, useEffect } from 'react';
import {
  Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Button, Dialog, DialogTitle, DialogContent, DialogActions, TextField,
  Chip, Box, Typography, IconButton, Tooltip
} from '@mui/material';
import { userAPI } from '../../services/api';
import toast from 'react-hot-toast';
import AddIcon from '@mui/icons-material/Add';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import PauseIcon from '@mui/icons-material/Pause';
import ArchiveIcon from '@mui/icons-material/Archive';
import RefreshIcon from '@mui/icons-material/Refresh';

function UsersPanel() {
  const [users, setUsers] = useState([]);
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    full_name: '',
    password: ''
  });

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const response = await userAPI.getAll();
      setUsers(response.data);
    } catch (error) {
      toast.error('Error loading users');
    }
  };

  const handleCreate = async () => {
    try {
      await userAPI.create(formData);
      toast.success('User created successfully');
      setOpen(false);
      setFormData({ email: '', username: '', full_name: '', password: '' });
      loadUsers();
    } catch (error) {
      toast.error('Error creating user');
    }
  };

  const handleActivate = async (id) => {
    try {
      await userAPI.activate(id);
      toast.success('User activated');
      loadUsers();
    } catch (error) {
      toast.error('Error activating user');
    }
  };

  const handleSuspend = async (id) => {
    try {
      await userAPI.suspend(id);
      toast.success('User suspended');
      loadUsers();
    } catch (error) {
      toast.error('Error suspending user');
    }
  };

  const handleArchive = async (id) => {
    try {
      await userAPI.archive(id);
      toast.success('User archived');
      loadUsers();
    } catch (error) {
      toast.error('Error archiving user');
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: 'warning',
      active: 'success',
      suspended: 'error',
      archived: 'default'
    };
    return colors[status] || 'default';
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">User Management</Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadUsers}
            sx={{ mr: 1 }}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpen(true)}
          >
            Create User
          </Button>
        </Box>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Username</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Full Name</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Created At</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users.map((user) => (
              <TableRow key={user.id}>
                <TableCell>{user.id}</TableCell>
                <TableCell>{user.username}</TableCell>
                <TableCell>{user.email}</TableCell>
                <TableCell>{user.full_name || '-'}</TableCell>
                <TableCell>
                  <Chip
                    label={user.status}
                    color={getStatusColor(user.status)}
                    size="small"
                  />
                </TableCell>
                <TableCell>{new Date(user.created_at).toLocaleDateString()}</TableCell>
                <TableCell align="right">
                  <Tooltip title="Activate">
                    <IconButton
                      size="small"
                      onClick={() => handleActivate(user.id)}
                      disabled={user.status === 'active'}
                      color="success"
                    >
                      <PlayArrowIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Suspend">
                    <IconButton
                      size="small"
                      onClick={() => handleSuspend(user.id)}
                      disabled={user.status === 'suspended' || user.status === 'archived'}
                      color="error"
                    >
                      <PauseIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Archive">
                    <IconButton
                      size="small"
                      onClick={() => handleArchive(user.id)}
                      disabled={user.status === 'archived'}
                    >
                      <ArchiveIcon />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New User</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Username"
            value={formData.username}
            onChange={(e) => setFormData({ ...formData, username: e.target.value })}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Full Name"
            value={formData.full_name}
            onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Password"
            type="password"
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            margin="normal"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button onClick={handleCreate} variant="contained">Create</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default UsersPanel;
