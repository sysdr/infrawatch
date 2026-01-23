import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Paper, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Chip, TextField, MenuItem
} from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { fetchChanges, fetchChangeStats } from '../services/api';

function ChangesView() {
  const [changes, setChanges] = useState([]);
  const [stats, setStats] = useState(null);
  const [timeRange, setTimeRange] = useState(24);

  useEffect(() => {
    loadData();
  }, [timeRange]);

  const loadData = async () => {
    const changesData = await fetchChanges(timeRange);
    const statsData = await fetchChangeStats();
    setChanges(changesData.changes || []);
    setStats(statsData);
  };

  const getChangeColor = (type) => {
    const colors = {
      'CREATED': 'success',
      'MODIFIED': 'warning',
      'DELETED': 'error'
    };
    return colors[type] || 'default';
  };

  const chartData = stats ? Object.entries(stats.by_type || {}).map(([name, value]) => ({
    name,
    value
  })) : [];

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" fontWeight="bold">
          Infrastructure Changes
        </Typography>
        <TextField
          select
          label="Time Range"
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value)}
          sx={{ minWidth: 150 }}
        >
          <MenuItem value={1}>Last Hour</MenuItem>
          <MenuItem value={24}>Last 24 Hours</MenuItem>
          <MenuItem value={168}>Last Week</MenuItem>
        </TextField>
      </Box>

      {stats && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" mb={2}>Change Statistics</Typography>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke="#1976d2" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </Paper>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow sx={{ bgcolor: '#f5f5f5' }}>
              <TableCell><strong>Resource ID</strong></TableCell>
              <TableCell><strong>Change Type</strong></TableCell>
              <TableCell><strong>Detected At</strong></TableCell>
              <TableCell><strong>Details</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {changes.map((change) => (
              <TableRow key={change.id} hover>
                <TableCell>{change.resource_id}</TableCell>
                <TableCell>
                  <Chip 
                    label={change.type} 
                    size="small" 
                    color={getChangeColor(change.type)} 
                  />
                </TableCell>
                <TableCell>
                  {new Date(change.detected_at).toLocaleString()}
                </TableCell>
                <TableCell>
                  <Typography variant="caption">
                    {change.diff?.changed_fields?.length || 0} fields changed
                  </Typography>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Typography variant="body2" color="textSecondary" mt={2}>
        Showing {changes.length} changes in the last {timeRange} hours
      </Typography>
    </Box>
  );
}

export default ChangesView;
