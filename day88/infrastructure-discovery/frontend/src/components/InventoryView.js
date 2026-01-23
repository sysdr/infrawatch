import React, { useState, useEffect } from 'react';
import {
  Box, Table, TableBody, TableCell, TableContainer, TableHead,
  TableRow, Paper, Chip, TextField, MenuItem, Typography,
  IconButton, Collapse
} from '@mui/material';
import { KeyboardArrowDown, KeyboardArrowUp } from '@mui/icons-material';
import { fetchResources } from '../services/api';

function ResourceRow({ resource }) {
  const [open, setOpen] = useState(false);

  const getStateColor = (state) => {
    const colors = {
      'DISCOVERED': 'info',
      'MODIFIED': 'warning',
      'TRACKED': 'success'
    };
    return colors[state] || 'default';
  };

  return (
    <>
      <TableRow hover>
        <TableCell>
          <IconButton size="small" onClick={() => setOpen(!open)}>
            {open ? <KeyboardArrowUp /> : <KeyboardArrowDown />}
          </IconButton>
        </TableCell>
        <TableCell>{resource.name}</TableCell>
        <TableCell>
          <Chip label={resource.type} size="small" color="primary" variant="outlined" />
        </TableCell>
        <TableCell>{resource.region}</TableCell>
        <TableCell>
          <Chip label={resource.state} size="small" color={getStateColor(resource.state)} />
        </TableCell>
        <TableCell>{new Date(resource.discovered_at).toLocaleString()}</TableCell>
      </TableRow>
      <TableRow>
        <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={6}>
          <Collapse in={open} timeout="auto" unmountOnExit>
            <Box sx={{ margin: 2, bgcolor: '#f5f5f5', p: 2, borderRadius: 1 }}>
              <Typography variant="subtitle2" gutterBottom>
                Resource Details
              </Typography>
              <Typography variant="body2">
                <strong>ID:</strong> {resource.id}
              </Typography>
              <Typography variant="body2">
                <strong>Provider:</strong> {resource.provider}
              </Typography>
              <Typography variant="body2" component="pre" sx={{ mt: 1, fontSize: '0.75rem' }}>
                {JSON.stringify(resource.metadata, null, 2)}
              </Typography>
            </Box>
          </Collapse>
        </TableCell>
      </TableRow>
    </>
  );
}

function InventoryView() {
  const [resources, setResources] = useState([]);
  const [filters, setFilters] = useState({ resource_type: '', region: '' });

  useEffect(() => {
    loadResources();
  }, [filters]);

  const loadResources = async () => {
    const cleanFilters = Object.fromEntries(
      Object.entries(filters).filter(([_, v]) => v !== '')
    );
    const data = await fetchResources(cleanFilters);
    setResources(data.resources || []);
  };

  const resourceTypes = [...new Set(resources.map(r => r.type))];
  const regions = [...new Set(resources.map(r => r.region))];

  return (
    <Box p={3}>
      <Typography variant="h5" fontWeight="bold" mb={3}>
        Resource Inventory
      </Typography>

      <Box display="flex" gap={2} mb={3}>
        <TextField
          select
          label="Resource Type"
          value={filters.resource_type}
          onChange={(e) => setFilters({ ...filters, resource_type: e.target.value })}
          sx={{ minWidth: 200 }}
        >
          <MenuItem value="">All Types</MenuItem>
          {resourceTypes.map(type => (
            <MenuItem key={type} value={type}>{type}</MenuItem>
          ))}
        </TextField>

        <TextField
          select
          label="Region"
          value={filters.region}
          onChange={(e) => setFilters({ ...filters, region: e.target.value })}
          sx={{ minWidth: 200 }}
        >
          <MenuItem value="">All Regions</MenuItem>
          {regions.map(region => (
            <MenuItem key={region} value={region}>{region}</MenuItem>
          ))}
        </TextField>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow sx={{ bgcolor: '#f5f5f5' }}>
              <TableCell />
              <TableCell><strong>Name</strong></TableCell>
              <TableCell><strong>Type</strong></TableCell>
              <TableCell><strong>Region</strong></TableCell>
              <TableCell><strong>State</strong></TableCell>
              <TableCell><strong>Discovered</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {resources.map((resource) => (
              <ResourceRow key={resource.id} resource={resource} />
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Typography variant="body2" color="textSecondary" mt={2}>
        Showing {resources.length} resources
      </Typography>
    </Box>
  );
}

export default InventoryView;
