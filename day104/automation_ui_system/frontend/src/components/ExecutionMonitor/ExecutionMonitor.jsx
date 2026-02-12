import React, { useState, useEffect } from 'react';
import { Box, Paper, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip, IconButton, Dialog, DialogTitle, DialogContent, Stack } from '@mui/material';
import VisibilityIcon from '@mui/icons-material/Visibility';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import ScheduleIcon from '@mui/icons-material/Schedule';
import { executionApi } from '../../services/api';
import wsService from '../../services/websocket';
import { format } from 'date-fns';
import { toast } from 'react-toastify';

const ExecutionMonitor = () => {
  const [executions, setExecutions] = useState([]);
  const [selectedExecution, setSelectedExecution] = useState(null);
  const [steps, setSteps] = useState([]);
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    loadExecutions();
    wsService.connect();
    wsService.on('workflow_update', () => loadExecutions());
    return () => wsService.off('workflow_update', loadExecutions);
  }, []);

  const loadExecutions = async () => {
    try {
      const res = await executionApi.getAll();
      setExecutions(res.data.executions || []);
    } catch (e) { console.error(e); }
  };

  const loadExecutionDetails = async (executionId) => {
    try {
      const [execRes, stepsRes] = await Promise.all([executionApi.getById(executionId), executionApi.getSteps(executionId)]);
      setSelectedExecution(execRes.data);
      setSteps(stepsRes.data.steps || []);
      setShowDetails(true);
    } catch (e) { toast.error('Failed to load details'); }
  };

  const getStatusIcon = (status) => {
    if (status === 'success') return <CheckCircleIcon color="success" />;
    if (status === 'failed') return <ErrorIcon color="error" />;
    return <ScheduleIcon color="primary" />;
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>Execution Monitor</Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell><TableCell>Workflow ID</TableCell><TableCell>Status</TableCell><TableCell>Trigger</TableCell><TableCell>Duration</TableCell><TableCell>Started At</TableCell><TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {executions.map((exec) => (
              <TableRow key={exec.id}>
                <TableCell>{exec.id}</TableCell>
                <TableCell>{exec.workflow_id}</TableCell>
                <TableCell><Chip label={exec.status} color={exec.status === 'success' ? 'success' : exec.status === 'failed' ? 'error' : 'default'} size="small" /></TableCell>
                <TableCell>{exec.trigger_type}</TableCell>
                <TableCell>{exec.duration_seconds != null ? `${exec.duration_seconds.toFixed(2)}s` : '-'}</TableCell>
                <TableCell>{exec.started_at ? format(new Date(exec.started_at), 'MMM d, HH:mm:ss') : '-'}</TableCell>
                <TableCell><IconButton onClick={() => loadExecutionDetails(exec.id)} size="small"><VisibilityIcon /></IconButton></TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <Dialog open={showDetails} onClose={() => setShowDetails(false)} maxWidth="md" fullWidth>
        <DialogTitle>Execution Details</DialogTitle>
        <DialogContent>
          {selectedExecution && (
            <Box sx={{ pt: 2 }}>
              <Typography variant="h6" gutterBottom>Execution #{selectedExecution.id}</Typography>
              <Typography variant="body2"><strong>Workflow ID:</strong> {selectedExecution.workflow_id} • <strong>Status:</strong> {selectedExecution.status} • <strong>Duration:</strong> {selectedExecution.duration_seconds?.toFixed(2)}s</Typography>
              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>Steps</Typography>
              <Stack spacing={0}>
                {steps.map((step, i) => (
                  <Box key={step.id} sx={{ display: 'flex', gap: 2, pb: i < steps.length - 1 ? 0 : 0 }}>
                    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                      <Box sx={{ width: 40, height: 40, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: step.status === 'success' ? 'success.main' : step.status === 'failed' ? 'error.main' : 'grey.400', color: 'white', '& .MuiSvgIcon-root': { color: 'white' } }}>
                        {getStatusIcon(step.status)}
                      </Box>
                      {i < steps.length - 1 && <Box sx={{ width: 2, flexGrow: 1, minHeight: 24, bgcolor: 'grey.300' }} />}
                    </Box>
                    <Paper sx={{ p: 2, mb: i < steps.length - 1 ? 2 : 0, flex: 1 }}>
                      <Typography variant="subtitle1">{step.step_name}</Typography>
                      <Typography variant="body2" color="textSecondary">Type: {step.step_type} • Duration: {step.duration_seconds?.toFixed(2)}s</Typography>
                      {step.error_message && <Typography variant="body2" color="error" sx={{ mt: 1 }}>Error: {step.error_message}</Typography>}
                    </Paper>
                  </Box>
                ))}
              </Stack>
            </Box>
          )}
        </DialogContent>
      </Dialog>
    </Box>
  );
};

export default ExecutionMonitor;
