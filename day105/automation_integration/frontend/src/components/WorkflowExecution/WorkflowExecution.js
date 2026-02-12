import React, { useState, useEffect } from 'react';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Chip from '@mui/material/Chip';
import Box from '@mui/material/Box';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import RefreshIcon from '@mui/icons-material/Refresh';

import { workflowsApi, executionsApi } from '../../services/api';
import { useWebSocket } from '../../hooks/useWebSocket';

function WorkflowExecution() {
  const [workflows, setWorkflows] = useState([]);
  const [executions, setExecutions] = useState([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState(null);
  const [inputData, setInputData] = useState('{}');
  const { messages } = useWebSocket();

  useEffect(() => {
    fetchWorkflows();
    fetchExecutions();
  }, []);

  useEffect(() => {
    // Handle WebSocket messages
    messages.forEach((msg) => {
      if (msg.type === 'execution_update') {
        fetchExecutions();
      }
    });
  }, [messages]);

  const fetchWorkflows = async () => {
    try {
      const response = await workflowsApi.list();
      setWorkflows(response.data);
    } catch (error) {
      console.error('Error fetching workflows:', error);
    }
  };

  const fetchExecutions = async () => {
    try {
      const response = await executionsApi.list();
      setExecutions(response.data);
    } catch (error) {
      console.error('Error fetching executions:', error);
    }
  };

  const handleExecute = async () => {
    if (!selectedWorkflow) {
      alert('Please select a workflow');
      return;
    }

    try {
      const input = JSON.parse(inputData);
      await executionsApi.create({
        workflow_id: selectedWorkflow.id,
        input_data: input,
      });
      fetchExecutions();
      setInputData('{}');
    } catch (error) {
      console.error('Error creating execution:', error);
      alert('Error creating execution');
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: 'default',
      running: 'primary',
      completed: 'success',
      failed: 'error',
      cancelled: 'warning',
    };
    return colors[status] || 'default';
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Create Execution
          </Typography>
          
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Select Workflow
            </Typography>
            {workflows.map((workflow) => (
              <Button
                key={workflow.id}
                variant={selectedWorkflow?.id === workflow.id ? 'contained' : 'outlined'}
                onClick={() => setSelectedWorkflow(workflow)}
                sx={{ mr: 1, mb: 1 }}
              >
                {workflow.name}
              </Button>
            ))}
          </Box>

          {selectedWorkflow && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Workflow: {selectedWorkflow.name}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {selectedWorkflow.description}
              </Typography>
            </Box>
          )}

          <TextField
            fullWidth
            multiline
            rows={4}
            label="Input Data (JSON)"
            value={inputData}
            onChange={(e) => setInputData(e.target.value)}
            sx={{ mt: 2 }}
          />

          <Button
            variant="contained"
            startIcon={<PlayArrowIcon />}
            onClick={handleExecute}
            sx={{ mt: 2 }}
            disabled={!selectedWorkflow}
          >
            Execute Workflow
          </Button>
        </Paper>
      </Grid>

      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 3 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">
              Recent Executions
            </Typography>
            <Button
              startIcon={<RefreshIcon />}
              onClick={fetchExecutions}
              size="small"
            >
              Refresh
            </Button>
          </Box>

          <Table sx={{ mt: 2 }} size="small">
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Time</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {executions.slice(0, 10).map((execution) => (
                <TableRow key={execution.id}>
                  <TableCell>{execution.id}</TableCell>
                  <TableCell>
                    <Chip
                      label={execution.status}
                      color={getStatusColor(execution.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {execution.execution_time ? `${execution.execution_time.toFixed(2)}s` : '-'}
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

export default WorkflowExecution;
