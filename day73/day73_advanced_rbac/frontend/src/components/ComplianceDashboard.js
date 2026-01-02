import React, { useState, useEffect } from 'react';
import {
  Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Typography, Box, Chip, Button, Alert
} from '@mui/material';
import { formatDistanceToNow } from 'date-fns';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

function ComplianceDashboard() {
  const [violations, setViolations] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadViolations();
  }, []);

  const loadViolations = async () => {
    try {
      const response = await axios.get(`${API_URL}/compliance/violations`);
      setViolations(response.data);
    } catch (error) {
      console.error('Error loading violations:', error);
    }
  };

  const runCheck = async () => {
    setLoading(true);
    try {
      await axios.post(`${API_URL}/compliance/check`);
      loadViolations();
    } catch (error) {
      console.error('Error running compliance check:', error);
    }
    setLoading(false);
  };

  const getSeverityColor = (severity) => {
    const colors = {
      low: 'info',
      medium: 'warning',
      high: 'error',
      critical: 'error'
    };
    return colors[severity] || 'default';
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5">Compliance Dashboard</Typography>
        <Button variant="contained" onClick={runCheck} disabled={loading}>
          Run Compliance Check
        </Button>
      </Box>

      {violations.length === 0 && (
        <Alert severity="success" sx={{ mb: 3 }}>
          No active compliance violations detected. System is compliant.
        </Alert>
      )}

      {violations.length > 0 && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          {violations.length} active compliance violation(s) detected
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Detected</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Severity</TableCell>
              <TableCell>Subject</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {violations.map((violation) => (
              <TableRow key={violation.id}>
                <TableCell>
                  {formatDistanceToNow(new Date(violation.detected_at), { addSuffix: true })}
                </TableCell>
                <TableCell>{violation.violation_type}</TableCell>
                <TableCell>
                  <Chip 
                    label={violation.severity}
                    color={getSeverityColor(violation.severity)}
                    size="small"
                  />
                </TableCell>
                <TableCell>{violation.subject_id}</TableCell>
                <TableCell>{violation.description}</TableCell>
                <TableCell>
                  <Chip 
                    label={violation.resolved_at ? 'Resolved' : 'Active'}
                    color={violation.resolved_at ? 'success' : 'error'}
                    size="small"
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

export default ComplianceDashboard;
