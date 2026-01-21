import React, { useState, useEffect } from 'react';
import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  TextField,
  Box,
  Typography
} from '@mui/material';
import { k8sApi } from '../../services/api';

function PodsView({ wsData }) {
  const [pods, setPods] = useState([]);
  const [filter, setFilter] = useState('');

  useEffect(() => {
    fetchPods();
  }, []);

  useEffect(() => {
    if (wsData && wsData.type === 'pod_update') {
      fetchPods();
    }
  }, [wsData]);

  const fetchPods = async () => {
    try {
      const response = await k8sApi.getPods();
      setPods(response.data);
    } catch (error) {
      console.error('Error fetching pods:', error);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Running': return 'success';
      case 'Pending': return 'warning';
      case 'Failed': return 'error';
      default: return 'default';
    }
  };

  const filteredPods = pods.filter(pod =>
    pod.name.toLowerCase().includes(filter.toLowerCase()) ||
    pod.namespace.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Pods
      </Typography>
      <TextField
        fullWidth
        variant="outlined"
        placeholder="Filter by name or namespace..."
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
        sx={{ mb: 2 }}
      />
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><strong>Name</strong></TableCell>
              <TableCell><strong>Namespace</strong></TableCell>
              <TableCell><strong>Status</strong></TableCell>
              <TableCell><strong>Node</strong></TableCell>
              <TableCell><strong>IP</strong></TableCell>
              <TableCell><strong>Restarts</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredPods.map((pod) => (
              <TableRow key={`${pod.namespace}-${pod.name}`} hover>
                <TableCell>{pod.name}</TableCell>
                <TableCell>{pod.namespace}</TableCell>
                <TableCell>
                  <Chip
                    label={pod.status}
                    color={getStatusColor(pod.status)}
                    size="small"
                  />
                </TableCell>
                <TableCell>{pod.node_name || '-'}</TableCell>
                <TableCell>{pod.ip || '-'}</TableCell>
                <TableCell>{pod.restart_count}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

export default PodsView;
