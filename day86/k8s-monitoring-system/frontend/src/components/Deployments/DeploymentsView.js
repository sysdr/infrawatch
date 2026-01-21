import React, { useState, useEffect } from 'react';
import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  Box,
  Typography
} from '@mui/material';
import { k8sApi } from '../../services/api';

function DeploymentsView({ wsData }) {
  const [deployments, setDeployments] = useState([]);

  useEffect(() => {
    fetchDeployments();
  }, []);

  useEffect(() => {
    if (wsData && wsData.type === 'deployment_update') {
      fetchDeployments();
    }
  }, [wsData]);

  const fetchDeployments = async () => {
    try {
      const response = await k8sApi.getDeployments();
      setDeployments(response.data);
    } catch (error) {
      console.error('Error fetching deployments:', error);
    }
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Deployments
      </Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><strong>Name</strong></TableCell>
              <TableCell><strong>Namespace</strong></TableCell>
              <TableCell><strong>Ready</strong></TableCell>
              <TableCell><strong>Strategy</strong></TableCell>
              <TableCell><strong>Image</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {deployments.map((deploy) => (
              <TableRow key={`${deploy.namespace}-${deploy.name}`} hover>
                <TableCell>{deploy.name}</TableCell>
                <TableCell>{deploy.namespace}</TableCell>
                <TableCell>
                  <Box>
                    <Typography variant="body2">
                      {deploy.ready_replicas}/{deploy.replicas}
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={(deploy.ready_replicas / deploy.replicas) * 100}
                      sx={{ mt: 0.5 }}
                    />
                  </Box>
                </TableCell>
                <TableCell>{deploy.strategy}</TableCell>
                <TableCell sx={{ maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {deploy.image}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

export default DeploymentsView;
