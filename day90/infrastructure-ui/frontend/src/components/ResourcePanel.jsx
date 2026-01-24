import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box, Paper, Typography, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Button, Dialog, DialogTitle, DialogContent,
  DialogActions, TextField, Select, MenuItem, FormControl, InputLabel,
  Chip, CircularProgress
} from '@mui/material';
import { Add, Refresh } from '@mui/icons-material';
import { fetchResources } from '../store/resourceSlice';
import { resourcesAPI } from '../services/api';

function ResourcePanel() {
  const dispatch = useDispatch();
  const { resources, loading } = useSelector(state => state.resources);
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    resource_type: 'ec2',
    cloud_provider: 'aws',
    region: 'us-east-1'
  });

  useEffect(() => {
    dispatch(fetchResources());
  }, [dispatch]);

  const handleCreate = async () => {
    try {
      await resourcesAPI.createResource(formData);
      setOpen(false);
      dispatch(fetchResources());
    } catch (error) {
      console.error('Failed to create resource:', error);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      running: 'success',
      stopped: 'default',
      provisioning: 'warning',
      error: 'error'
    };
    return colors[status] || 'default';
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Paper elevation={3} sx={{ p: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h5">Resources</Typography>
          <Box>
            <Button
              startIcon={<Refresh />}
              onClick={() => dispatch(fetchResources())}
              sx={{ mr: 1 }}
            >
              Refresh
            </Button>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => setOpen(true)}
            >
              Create Resource
            </Button>
          </Box>
        </Box>

        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Provider</TableCell>
                <TableCell>Region</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Tags</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {resources.items?.map((resource) => (
                <TableRow key={resource.id} hover>
                  <TableCell>{resource.name}</TableCell>
                  <TableCell>{resource.type}</TableCell>
                  <TableCell>{resource.provider}</TableCell>
                  <TableCell>{resource.region}</TableCell>
                  <TableCell>
                    <Chip
                      label={resource.status}
                      color={getStatusColor(resource.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {Object.entries(resource.tags || {}).slice(0, 2).map(([key, value]) => (
                      <Chip key={key} label={`${key}:${value}`} size="small" sx={{ mr: 0.5 }} />
                    ))}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          Total: {resources.total} resources
        </Typography>
      </Paper>

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Resource</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              label="Name"
              fullWidth
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            />
            <FormControl fullWidth>
              <InputLabel>Type</InputLabel>
              <Select
                value={formData.resource_type}
                onChange={(e) => setFormData({ ...formData, resource_type: e.target.value })}
              >
                <MenuItem value="ec2">EC2 Instance</MenuItem>
                <MenuItem value="rds">RDS Database</MenuItem>
                <MenuItem value="elb">Load Balancer</MenuItem>
              </Select>
            </FormControl>
            <FormControl fullWidth>
              <InputLabel>Provider</InputLabel>
              <Select
                value={formData.cloud_provider}
                onChange={(e) => setFormData({ ...formData, cloud_provider: e.target.value })}
              >
                <MenuItem value="aws">AWS</MenuItem>
                <MenuItem value="gcp">GCP</MenuItem>
                <MenuItem value="azure">Azure</MenuItem>
              </Select>
            </FormControl>
            <FormControl fullWidth>
              <InputLabel>Region</InputLabel>
              <Select
                value={formData.region}
                onChange={(e) => setFormData({ ...formData, region: e.target.value })}
              >
                <MenuItem value="us-east-1">US East 1</MenuItem>
                <MenuItem value="us-west-2">US West 2</MenuItem>
                <MenuItem value="eu-west-1">EU West 1</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleCreate}>Create</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default ResourcePanel;
