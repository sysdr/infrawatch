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
  Box,
  Typography
} from '@mui/material';
import { k8sApi } from '../../services/api';

function NodesView({ wsData }) {
  const [nodes, setNodes] = useState([]);

  useEffect(() => {
    fetchNodes();
  }, []);

  useEffect(() => {
    if (wsData && wsData.type === 'node_update') {
      fetchNodes();
    }
  }, [wsData]);

  const fetchNodes = async () => {
    try {
      const response = await k8sApi.getNodes();
      setNodes(response.data);
    } catch (error) {
      console.error('Error fetching nodes:', error);
    }
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Nodes
      </Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><strong>Name</strong></TableCell>
              <TableCell><strong>Status</strong></TableCell>
              <TableCell><strong>Roles</strong></TableCell>
              <TableCell><strong>CPU</strong></TableCell>
              <TableCell><strong>Memory</strong></TableCell>
              <TableCell><strong>OS</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {nodes.map((node) => (
              <TableRow key={node.name} hover>
                <TableCell>{node.name}</TableCell>
                <TableCell>
                  <Chip
                    label={node.status}
                    color={node.status === 'Ready' ? 'success' : 'error'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {node.roles?.map(role => (
                    <Chip key={role} label={role} size="small" sx={{ mr: 0.5 }} />
                  ))}
                </TableCell>
                <TableCell>
                  {node.allocatable_cpu.toFixed(1)} / {node.capacity_cpu.toFixed(1)} cores
                </TableCell>
                <TableCell>
                  {(node.allocatable_memory / 1024).toFixed(1)} / {(node.capacity_memory / 1024).toFixed(1)} GB
                </TableCell>
                <TableCell>{node.os_image}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

export default NodesView;
