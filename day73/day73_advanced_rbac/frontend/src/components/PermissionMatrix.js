import React, { useState, useEffect } from 'react';
import {
  Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Button, TextField, Box, Typography, Chip, Alert
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

function PermissionMatrix() {
  const [evaluation, setEvaluation] = useState(null);
  const [request, setRequest] = useState({
    subject_id: 'user:1',
    action: 'read',
    resource_type: 'project',
    resource_id: '42'
  });

  const handleEvaluate = async () => {
    try {
      const response = await axios.post(`${API_URL}/permissions/evaluate`, request);
      setEvaluation(response.data);
    } catch (error) {
      console.error('Error evaluating permission:', error);
    }
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>Permission Evaluator</Typography>
      
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', gap: 2, mb: 2, flexWrap: 'wrap' }}>
          <TextField
            label="Subject ID"
            value={request.subject_id}
            onChange={(e) => setRequest({...request, subject_id: e.target.value})}
            placeholder="user:1"
          />
          <TextField
            label="Action"
            value={request.action}
            onChange={(e) => setRequest({...request, action: e.target.value})}
            placeholder="read"
          />
          <TextField
            label="Resource Type"
            value={request.resource_type}
            onChange={(e) => setRequest({...request, resource_type: e.target.value})}
            placeholder="project"
          />
          <TextField
            label="Resource ID"
            value={request.resource_id}
            onChange={(e) => setRequest({...request, resource_id: e.target.value})}
            placeholder="42"
          />
        </Box>
        
        <Button variant="contained" onClick={handleEvaluate}>
          Evaluate Permission
        </Button>
      </Paper>

      {evaluation && (
        <Alert 
          severity={evaluation.allowed ? "success" : "error"}
          icon={evaluation.allowed ? <CheckCircleIcon /> : <CancelIcon />}
          sx={{ mb: 2 }}
        >
          <Typography variant="h6">
            {evaluation.allowed ? 'Access Granted' : 'Access Denied'}
          </Typography>
          <Typography variant="body2">Reason: {evaluation.reason}</Typography>
          <Typography variant="body2">Policy: {evaluation.policy_matched}</Typography>
        </Alert>
      )}

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>Common Test Scenarios</Typography>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Subject</TableCell>
                <TableCell>Action</TableCell>
                <TableCell>Resource</TableCell>
                <TableCell>Expected Result</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              <TableRow>
                <TableCell>user:1</TableCell>
                <TableCell>read</TableCell>
                <TableCell>project:42</TableCell>
                <TableCell><Chip label="Allowed" color="success" size="small" /></TableCell>
              </TableRow>
              <TableRow>
                <TableCell>user:1</TableCell>
                <TableCell>delete</TableCell>
                <TableCell>project:42 (owned)</TableCell>
                <TableCell><Chip label="Allowed" color="success" size="small" /></TableCell>
              </TableRow>
              <TableRow>
                <TableCell>user:1</TableCell>
                <TableCell>admin</TableCell>
                <TableCell>project:99</TableCell>
                <TableCell><Chip label="Denied" color="error" size="small" /></TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
}

export default PermissionMatrix;
