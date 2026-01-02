import React, { useState, useEffect } from 'react';
import {
  Paper, TextField, Button, Box, Typography, Select, MenuItem,
  FormControl, InputLabel, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, IconButton
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

function PolicyEditor() {
  const [policies, setPolicies] = useState([]);
  const [newPolicy, setNewPolicy] = useState({
    name: '',
    subject_type: 'user',
    subject_id: '',
    action: 'read',
    resource_type: 'project',
    resource_id: '*',
    effect: 'allow',
    priority: 0
  });

  useEffect(() => {
    loadPolicies();
  }, []);

  const loadPolicies = async () => {
    try {
      const response = await axios.get(`${API_URL}/policies`);
      setPolicies(response.data);
    } catch (error) {
      console.error('Error loading policies:', error);
    }
  };

  const handleCreate = async () => {
    try {
      await axios.post(`${API_URL}/policies`, newPolicy);
      setNewPolicy({
        name: '',
        subject_type: 'user',
        subject_id: '',
        action: 'read',
        resource_type: 'project',
        resource_id: '*',
        effect: 'allow',
        priority: 0
      });
      loadPolicies();
    } catch (error) {
      console.error('Error creating policy:', error);
    }
  };

  const handleDelete = async (policyId) => {
    try {
      await axios.delete(`${API_URL}/policies/${policyId}`);
      loadPolicies();
    } catch (error) {
      console.error('Error deleting policy:', error);
    }
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>Policy Editor</Typography>
      
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>Create New Policy</Typography>
        <Box sx={{ display: 'flex', gap: 2, mb: 2, flexWrap: 'wrap' }}>
          <TextField
            label="Policy Name"
            value={newPolicy.name}
            onChange={(e) => setNewPolicy({...newPolicy, name: e.target.value})}
            sx={{ minWidth: 200 }}
          />
          
          <FormControl sx={{ minWidth: 120 }}>
            <InputLabel>Subject Type</InputLabel>
            <Select
              value={newPolicy.subject_type}
              label="Subject Type"
              onChange={(e) => setNewPolicy({...newPolicy, subject_type: e.target.value})}
            >
              <MenuItem value="user">User</MenuItem>
              <MenuItem value="role">Role</MenuItem>
              <MenuItem value="team">Team</MenuItem>
            </Select>
          </FormControl>
          
          <TextField
            label="Subject ID"
            value={newPolicy.subject_id}
            onChange={(e) => setNewPolicy({...newPolicy, subject_id: e.target.value})}
          />
          
          <FormControl sx={{ minWidth: 120 }}>
            <InputLabel>Action</InputLabel>
            <Select
              value={newPolicy.action}
              label="Action"
              onChange={(e) => setNewPolicy({...newPolicy, action: e.target.value})}
            >
              <MenuItem value="read">Read</MenuItem>
              <MenuItem value="write">Write</MenuItem>
              <MenuItem value="delete">Delete</MenuItem>
              <MenuItem value="admin">Admin</MenuItem>
              <MenuItem value="*">All (*)</MenuItem>
            </Select>
          </FormControl>
          
          <TextField
            label="Resource Type"
            value={newPolicy.resource_type}
            onChange={(e) => setNewPolicy({...newPolicy, resource_type: e.target.value})}
          />
          
          <TextField
            label="Resource ID"
            value={newPolicy.resource_id}
            onChange={(e) => setNewPolicy({...newPolicy, resource_id: e.target.value})}
          />
          
          <FormControl sx={{ minWidth: 120 }}>
            <InputLabel>Effect</InputLabel>
            <Select
              value={newPolicy.effect}
              label="Effect"
              onChange={(e) => setNewPolicy({...newPolicy, effect: e.target.value})}
            >
              <MenuItem value="allow">Allow</MenuItem>
              <MenuItem value="deny">Deny</MenuItem>
            </Select>
          </FormControl>
          
          <TextField
            label="Priority"
            type="number"
            value={newPolicy.priority != null ? newPolicy.priority : ''}
            onChange={(e) => {
              const val = e.target.value === '' ? 0 : parseInt(e.target.value, 10);
              setNewPolicy({...newPolicy, priority: isNaN(val) ? 0 : val});
            }}
            sx={{ width: 100 }}
          />
        </Box>
        
        <Button variant="contained" onClick={handleCreate}>
          Create Policy
        </Button>
      </Paper>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>Active Policies ({policies.length})</Typography>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Subject</TableCell>
                <TableCell>Action</TableCell>
                <TableCell>Resource</TableCell>
                <TableCell>Effect</TableCell>
                <TableCell>Priority</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {policies.map((policy) => (
                <TableRow key={policy.id}>
                  <TableCell>{policy.name}</TableCell>
                  <TableCell>{policy.subject_type}:{policy.subject_id}</TableCell>
                  <TableCell>{policy.action}</TableCell>
                  <TableCell>{policy.resource_type}:{policy.resource_id}</TableCell>
                  <TableCell>{policy.effect}</TableCell>
                  <TableCell>{policy.priority}</TableCell>
                  <TableCell>
                    <IconButton onClick={() => handleDelete(policy.id)} size="small">
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
}

export default PolicyEditor;
