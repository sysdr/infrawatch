import React, { useState, useEffect } from 'react';
import {
  Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Typography, Box, Chip, TextField, Button
} from '@mui/material';
import { formatDistanceToNow } from 'date-fns';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

function AuditLog() {
  const [events, setEvents] = useState([]);
  const [stats, setStats] = useState(null);
  const [filter, setFilter] = useState({ subject_id: '', resource_type: '', decision: '' });

  useEffect(() => {
    loadEvents();
    loadStats();
    const interval = setInterval(() => {
      loadEvents();
      loadStats();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadEvents = async () => {
    try {
      const params = new URLSearchParams();
      if (filter.subject_id) params.append('subject_id', filter.subject_id);
      if (filter.resource_type) params.append('resource_type', filter.resource_type);
      if (filter.decision) params.append('decision', filter.decision);
      
      const response = await axios.get(`${API_URL}/audit/events?limit=50&${params}`);
      setEvents(response.data);
    } catch (error) {
      console.error('Error loading events:', error);
    }
  };

  const loadStats = async () => {
    try {
      const response = await axios.get(`${API_URL}/audit/stats?time_range_hours=24`);
      setStats(response.data);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const handleFilter = () => {
    loadEvents();
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>Audit Log</Typography>
      
      {stats && (
        <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
          <Paper sx={{ p: 2, flex: 1 }}>
            <Typography variant="h4">{stats.total_checks}</Typography>
            <Typography color="textSecondary">Total Checks (24h)</Typography>
          </Paper>
          <Paper sx={{ p: 2, flex: 1 }}>
            <Typography variant="h4" color="success.main">{stats.allowed}</Typography>
            <Typography color="textSecondary">Allowed</Typography>
          </Paper>
          <Paper sx={{ p: 2, flex: 1 }}>
            <Typography variant="h4" color="error.main">{stats.denied}</Typography>
            <Typography color="textSecondary">Denied</Typography>
          </Paper>
          <Paper sx={{ p: 2, flex: 1 }}>
            <Typography variant="h4">{stats.deny_rate.toFixed(1)}%</Typography>
            <Typography color="textSecondary">Deny Rate</Typography>
          </Paper>
        </Box>
      )}

      <Paper sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <TextField
            label="Subject ID"
            size="small"
            value={filter.subject_id}
            onChange={(e) => setFilter({...filter, subject_id: e.target.value})}
          />
          <TextField
            label="Resource Type"
            size="small"
            value={filter.resource_type}
            onChange={(e) => setFilter({...filter, resource_type: e.target.value})}
          />
          <TextField
            label="Decision"
            size="small"
            value={filter.decision}
            onChange={(e) => setFilter({...filter, decision: e.target.value})}
          />
          <Button variant="contained" onClick={handleFilter}>Filter</Button>
          <Button onClick={() => { setFilter({ subject_id: '', resource_type: '', decision: '' }); loadEvents(); }}>
            Clear
          </Button>
        </Box>
      </Paper>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Time</TableCell>
              <TableCell>Subject</TableCell>
              <TableCell>Action</TableCell>
              <TableCell>Resource</TableCell>
              <TableCell>Decision</TableCell>
              <TableCell>Reason</TableCell>
              <TableCell>Policy</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {events.map((event) => (
              <TableRow key={event.id}>
                <TableCell>
                  {formatDistanceToNow(new Date(event.timestamp), { addSuffix: true })}
                </TableCell>
                <TableCell>{event.subject_type}:{event.subject_id}</TableCell>
                <TableCell>{event.action}</TableCell>
                <TableCell>{event.resource_type}:{event.resource_id}</TableCell>
                <TableCell>
                  <Chip 
                    label={event.decision}
                    color={event.decision === 'allowed' ? 'success' : 'error'}
                    size="small"
                  />
                </TableCell>
                <TableCell>{event.reason}</TableCell>
                <TableCell>{event.policy_matched}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

export default AuditLog;
