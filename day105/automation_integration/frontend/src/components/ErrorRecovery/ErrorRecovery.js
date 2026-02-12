import React, { useState, useEffect } from 'react';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Button from '@mui/material/Button';
import Chip from '@mui/material/Chip';
import Box from '@mui/material/Box';
import RefreshIcon from '@mui/icons-material/Refresh';
import ReplayIcon from '@mui/icons-material/Replay';
import { executionsApi } from '../../services/api';

function ErrorRecovery() {
  const [failedExecutions, setFailedExecutions] = useState([]);

  useEffect(() => {
    fetchFailedExecutions();
  }, []);

  const fetchFailedExecutions = async () => {
    try {
      const response = await executionsApi.list('failed');
      setFailedExecutions(response.data);
    } catch (error) {
      console.error('Error fetching failed executions:', error);
    }
  };

  const handleRetry = async (executionId) => {
    try {
      await executionsApi.retry(executionId);
      fetchFailedExecutions();
      alert('Execution retry submitted');
    } catch (error) {
      console.error('Error retrying execution:', error);
      alert('Error retrying execution');
    }
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Paper sx={{ p: 3 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">
              Failed Executions - Error Recovery
            </Typography>
            <Button
              startIcon={<RefreshIcon />}
              onClick={fetchFailedExecutions}
              variant="outlined"
            >
              Refresh
            </Button>
          </Box>

          <Table sx={{ mt: 2 }}>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Workflow ID</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Error</TableCell>
                <TableCell>Retry Count</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {failedExecutions.map((execution) => (
                <TableRow key={execution.id}>
                  <TableCell>{execution.id}</TableCell>
                  <TableCell>{execution.workflow_id}</TableCell>
                  <TableCell>
                    <Chip label={execution.status} color="error" size="small" />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" noWrap sx={{ maxWidth: 300 }}>
                      {execution.error_message || '-'}
                    </Typography>
                  </TableCell>
                  <TableCell>{execution.retry_count}</TableCell>
                  <TableCell>
                    <Button
                      size="small"
                      variant="contained"
                      startIcon={<ReplayIcon />}
                      onClick={() => handleRetry(execution.id)}
                      disabled={execution.retry_count >= 3}
                    >
                      Retry
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          {failedExecutions.length === 0 && (
            <Box sx={{ mt: 4, textAlign: 'center' }}>
              <Typography color="textSecondary">
                No failed executions found
              </Typography>
            </Box>
          )}
        </Paper>
      </Grid>
    </Grid>
  );
}

export default ErrorRecovery;
