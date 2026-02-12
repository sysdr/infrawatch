import React, { useState, useEffect } from 'react';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Chip from '@mui/material/Chip';
import SecurityIcon from '@mui/icons-material/Security';
import WarningIcon from '@mui/icons-material/Warning';
import { securityApi } from '../../services/api';

function SecurityValidation() {
  const [stats, setStats] = useState(null);
  const [violations, setViolations] = useState([]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [statsRes, violationsRes] = await Promise.all([
        securityApi.getStats(),
        securityApi.listViolations(),
      ]);
      setStats(statsRes.data);
      setViolations(violationsRes.data);
    } catch (error) {
      console.error('Error fetching security data:', error);
    }
  };

  if (!stats) {
    return <Typography>Loading...</Typography>;
  }

  const getSeverityColor = (severity) => {
    const colors = {
      low: 'info',
      medium: 'warning',
      high: 'error',
      critical: 'error',
    };
    return colors[severity] || 'default';
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ bgcolor: '#e3f2fd' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Total Checks
                </Typography>
                <Typography variant="h4">{stats.total_checks}</Typography>
              </Box>
              <SecurityIcon sx={{ fontSize: 48, color: '#1976d2' }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ bgcolor: '#e8f5e9' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Passed
                </Typography>
                <Typography variant="h4">{stats.passed_checks}</Typography>
              </Box>
              <SecurityIcon sx={{ fontSize: 48, color: '#4caf50' }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ bgcolor: '#ffebee' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Failed
                </Typography>
                <Typography variant="h4">{stats.failed_checks}</Typography>
              </Box>
              <WarningIcon sx={{ fontSize: 48, color: '#f44336' }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ bgcolor: '#fff3e0' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Violations
                </Typography>
                <Typography variant="h4">{stats.total_violations}</Typography>
              </Box>
              <WarningIcon sx={{ fontSize: 48, color: '#ff9800' }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Recent Security Violations
          </Typography>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Execution ID</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Severity</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Timestamp</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {violations.map((violation) => (
                <TableRow key={violation.id}>
                  <TableCell>{violation.execution_id}</TableCell>
                  <TableCell>{violation.violation_type}</TableCell>
                  <TableCell>
                    <Chip
                      label={violation.severity}
                      color={getSeverityColor(violation.severity)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{violation.description}</TableCell>
                  <TableCell>
                    {new Date(violation.timestamp).toLocaleString()}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Paper>
      </Grid>
    </Grid>
  );
}

export default SecurityValidation;
