import React, { useState, useEffect } from 'react';
import { Paper, Typography, Box, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, TextField, Button, Chip } from '@mui/material';
import { auditApi } from '../services/api';

function AuditTrail() {
  const [auditEvents, setAuditEvents] = useState([]);
  const [filters, setFilters] = useState({ user_id: '', resource: '' });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAuditTrail();
  }, []);

  const loadAuditTrail = async () => {
    try {
      const response = await auditApi.getTrail({ ...filters, limit: 50 });
      setAuditEvents(response.data.audit_trail || []);
      setLoading(false);
    } catch (error) {
      console.error('Error loading audit trail:', error);
      setLoading(false);
    }
  };

  const handleSearch = () => {
    loadAuditTrail();
  };

  if (loading) {
    return <Typography>Loading audit trail...</Typography>;
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Audit Trail
      </Typography>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box display="flex" gap={2} alignItems="center">
          <TextField
            label="User ID"
            size="small"
            value={filters.user_id}
            onChange={(e) => setFilters({ ...filters, user_id: e.target.value })}
          />
          <TextField
            label="Resource"
            size="small"
            value={filters.resource}
            onChange={(e) => setFilters({ ...filters, resource: e.target.value })}
          />
          <Button variant="contained" onClick={handleSearch}>
            Search
          </Button>
        </Box>
      </Paper>

      {/* Audit Events Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Timestamp</TableCell>
              <TableCell>Event Type</TableCell>
              <TableCell>User</TableCell>
              <TableCell>Action</TableCell>
              <TableCell>Resource</TableCell>
              <TableCell>Result</TableCell>
              <TableCell>IP Address</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {auditEvents.map((event, idx) => (
              <TableRow key={idx}>
                <TableCell>{new Date(event.timestamp).toLocaleString()}</TableCell>
                <TableCell>{event.event_type}</TableCell>
                <TableCell>{event.username || event.user_id || 'N/A'}</TableCell>
                <TableCell>{event.action || 'N/A'}</TableCell>
                <TableCell>{event.resource || 'N/A'}</TableCell>
                <TableCell>
                  <Chip
                    label={event.result}
                    color={event.result === 'success' ? 'success' : 'error'}
                    size="small"
                  />
                </TableCell>
                <TableCell>{event.ip_address}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

export default AuditTrail;
