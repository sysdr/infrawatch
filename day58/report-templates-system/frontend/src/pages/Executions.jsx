import React, { useEffect, useState } from 'react';
import { Box, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Chip, IconButton, Alert, CircularProgress } from '@mui/material';
import { Download } from '@mui/icons-material';
import { reportApi } from '../services/api';

export default function Executions() {
  const [executions, setExecutions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadExecutions();
    const interval = setInterval(loadExecutions, 5000); // Refresh every 5s
    return () => clearInterval(interval);
  }, []);

  const loadExecutions = async () => {
    try {
      setError(null);
      const response = await reportApi.getExecutions();
      console.log('Executions response:', response.data);
      const executionsData = response.data || [];
      // Sort by id descending to show newest first
      executionsData.sort((a, b) => b.id - a.id);
      setExecutions(executionsData);
    } catch (error) {
      console.error('Failed to load executions:', error);
      setError(error.response?.data?.detail || error.message || 'Failed to load executions');
      setExecutions([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (executionId) => {
    try {
      const response = await reportApi.download(executionId);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `report_${executionId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Failed to download report:', error);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      completed: 'success',
      processing: 'info',
      failed: 'error',
      pending: 'warning'
    };
    return colors[status] || 'default';
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Report Executions
      </Typography>

      {loading && (
        <Box display="flex" justifyContent="center" p={3}>
          <CircularProgress />
        </Box>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {!loading && !error && executions.length === 0 && (
        <Alert severity="info" sx={{ mb: 2 }}>
          No executions found. Generate a report from the Schedules tab to see executions here.
        </Alert>
      )}

      {!loading && executions.length > 0 && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Schedule ID</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Started</TableCell>
                <TableCell>Completed</TableCell>
                <TableCell>Execution Time</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {executions.map((execution) => (
                <TableRow key={execution.id}>
                  <TableCell>{execution.id}</TableCell>
                  <TableCell>{execution.scheduled_report_id || '-'}</TableCell>
                  <TableCell>
                    <Chip
                      label={execution.status}
                      color={getStatusColor(execution.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{execution.started_at ? new Date(execution.started_at).toLocaleString() : '-'}</TableCell>
                  <TableCell>
                    {execution.completed_at ? new Date(execution.completed_at).toLocaleString() : '-'}
                  </TableCell>
                  <TableCell>{execution.execution_time ? `${execution.execution_time}s` : '-'}</TableCell>
                  <TableCell>
                    {execution.status === 'completed' && (
                      <IconButton onClick={() => handleDownload(execution.id)} size="small">
                        <Download />
                      </IconButton>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
}
