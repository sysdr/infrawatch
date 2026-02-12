import React, { useState, useEffect } from 'react';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Box from '@mui/material/Box';
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import SearchIcon from '@mui/icons-material/Search';
import { executionsApi } from '../../services/api';

function ExecutionMonitoring() {
  const [executionId, setExecutionId] = useState('');
  const [execution, setExecution] = useState(null);
  const [steps, setSteps] = useState([]);
  const [logs, setLogs] = useState([]);

  const handleSearch = async () => {
    if (!executionId) return;

    try {
      const [execRes, stepsRes, logsRes] = await Promise.all([
        executionsApi.get(executionId),
        executionsApi.getSteps(executionId),
        executionsApi.getLogs(executionId),
      ]);
      setExecution(execRes.data);
      setSteps(stepsRes.data);
      setLogs(logsRes.data);
    } catch (error) {
      console.error('Error fetching execution details:', error);
      alert('Execution not found');
    }
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Execution Monitoring
          </Typography>
          
          <Box display="flex" gap={2} sx={{ mt: 2 }}>
            <TextField
              label="Execution ID"
              value={executionId}
              onChange={(e) => setExecutionId(e.target.value)}
              size="small"
              sx={{ flexGrow: 1 }}
            />
            <Button
              variant="contained"
              startIcon={<SearchIcon />}
              onClick={handleSearch}
            >
              Search
            </Button>
          </Box>
        </Paper>
      </Grid>

      {execution && (
        <>
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Execution Details
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Typography><strong>ID:</strong> {execution.id}</Typography>
                <Typography><strong>Workflow ID:</strong> {execution.workflow_id}</Typography>
                <Typography><strong>Status:</strong> {execution.status}</Typography>
                <Typography><strong>Execution Time:</strong> {execution.execution_time ? `${execution.execution_time.toFixed(2)}s` : '-'}</Typography>
                <Typography><strong>Retry Count:</strong> {execution.retry_count}</Typography>
              </Box>
            </Paper>
          </Grid>

          <Grid item xs={12}>
            <Accordion defaultExpanded>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6">Execution Steps ({steps.length})</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Step Name</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Time</TableCell>
                      <TableCell>Retry Count</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {steps.map((step) => (
                      <TableRow key={step.id}>
                        <TableCell>{step.step_name}</TableCell>
                        <TableCell>{step.step_type}</TableCell>
                        <TableCell>{step.status}</TableCell>
                        <TableCell>
                          {step.execution_time ? `${step.execution_time.toFixed(2)}s` : '-'}
                        </TableCell>
                        <TableCell>{step.retry_count}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </AccordionDetails>
            </Accordion>
          </Grid>

          <Grid item xs={12}>
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6">Execution Logs ({logs.length})</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
                  {logs.map((log) => (
                    <Box
                      key={log.id}
                      sx={{
                        p: 1,
                        mb: 1,
                        bgcolor: log.level === 'ERROR' ? '#ffebee' : '#f5f5f5',
                        borderRadius: 1,
                      }}
                    >
                      <Typography variant="caption" color="textSecondary">
                        {new Date(log.timestamp).toLocaleString()} - {log.level}
                        {log.step_name && ` - ${log.step_name}`}
                      </Typography>
                      <Typography variant="body2">{log.message}</Typography>
                    </Box>
                  ))}
                </Box>
              </AccordionDetails>
            </Accordion>
          </Grid>
        </>
      )}
    </Grid>
  );
}

export default ExecutionMonitoring;
