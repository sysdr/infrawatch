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

function ServicesView({ wsData }) {
  const [services, setServices] = useState([]);

  useEffect(() => {
    fetchServices();
  }, []);

  useEffect(() => {
    if (wsData && wsData.type === 'service_update') {
      fetchServices();
    }
  }, [wsData]);

  const fetchServices = async () => {
    try {
      const response = await k8sApi.getServices();
      setServices(response.data);
    } catch (error) {
      console.error('Error fetching services:', error);
    }
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Services
      </Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><strong>Name</strong></TableCell>
              <TableCell><strong>Namespace</strong></TableCell>
              <TableCell><strong>Type</strong></TableCell>
              <TableCell><strong>Cluster IP</strong></TableCell>
              <TableCell><strong>External IP</strong></TableCell>
              <TableCell><strong>Ports</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {services.map((svc) => (
              <TableRow key={`${svc.namespace}-${svc.name}`} hover>
                <TableCell>{svc.name}</TableCell>
                <TableCell>{svc.namespace}</TableCell>
                <TableCell>
                  <Chip label={svc.type} size="small" variant="outlined" />
                </TableCell>
                <TableCell>{svc.cluster_ip}</TableCell>
                <TableCell>{svc.external_ip || '-'}</TableCell>
                <TableCell>
                  {svc.ports?.map(p => `${p.port}/${p.protocol}`).join(', ')}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

export default ServicesView;
