import { useState, useEffect } from 'react';
import {
  Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Chip, IconButton, Box, Typography, Dialog, DialogTitle, DialogContent,
  DialogActions, Button, Alert
} from '@mui/material';
import { Visibility, Undo } from '@mui/icons-material';
import { format } from 'date-fns';
import { api } from '../services/api';
import type { RemediationAction } from '../types';

const statusColors: Record<string, object> = {
  pending: { bgcolor: '#fff3e0', color: '#ff9800' },
  approved: { bgcolor: '#e8f5e9', color: '#4caf50' },
  executing: { bgcolor: '#e3f2fd', color: '#2196f3' },
  completed: { bgcolor: '#e8f5e9', color: '#4caf50' },
  failed: { bgcolor: '#ffebee', color: '#f44336' },
  rolled_back: { bgcolor: '#fff3e0', color: '#ff9800' }
};

export default function ActionsList() {
  const [actions, setActions] = useState<RemediationAction[]>([]);
  const [selectedAction, setSelectedAction] = useState<any>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [rollbackResult, setRollbackResult] = useState<string | null>(null);

  useEffect(() => {
    loadActions();
    const interval = setInterval(loadActions, 3000);
    return () => clearInterval(interval);
  }, []);

  const loadActions = async () => {
    try {
      const { data } = await api.getActions();
      setActions(data);
    } catch (e) {
      console.error('Failed to load actions:', e);
    }
  };

  const handleViewDetails = async (action: RemediationAction) => {
    try {
      const { data } = await api.getAction(action.id);
      setSelectedAction(data);
      setDetailsOpen(true);
    } catch (e) {
      console.error('Failed to load action details:', e);
    }
  };

  const handleRollback = async () => {
    if (!selectedAction) return;
    try {
      await api.rollbackAction(selectedAction.id);
      setRollbackResult('Rollback successful');
      setTimeout(() => {
        setRollbackResult(null);
        setDetailsOpen(false);
        loadActions();
      }, 2000);
    } catch {
      setRollbackResult('Rollback failed');
    }
  };

  const getRiskColor = (score: number) => {
    if (score < 30) return '#4caf50';
    if (score < 60) return '#ff9800';
    return '#f44336';
  };

  return (
    <>
      <TableContainer component={Paper}>
        <Table>
          <TableHead sx={{ bgcolor: '#f5f5f5' }}>
            <TableRow>
              <TableCell><strong>ID</strong></TableCell>
              <TableCell><strong>Template</strong></TableCell>
              <TableCell><strong>Incident</strong></TableCell>
              <TableCell><strong>Status</strong></TableCell>
              <TableCell><strong>Risk Score</strong></TableCell>
              <TableCell><strong>Blast Radius</strong></TableCell>
              <TableCell><strong>Created</strong></TableCell>
              <TableCell><strong>Actions</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {actions.map((action) => (
              <TableRow key={action.id} hover>
                <TableCell>{action.id}</TableCell>
                <TableCell>{action.template_name}</TableCell>
                <TableCell>
                  <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                    {action.incident_id}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip
                    label={String(action.status).toUpperCase()}
                    size="small"
                    sx={statusColors[action.status] || {}}
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={action.risk_score}
                    size="small"
                    sx={{ bgcolor: getRiskColor(action.risk_score), color: 'white' }}
                  />
                </TableCell>
                <TableCell>{action.blast_radius}</TableCell>
                <TableCell>{format(new Date(action.created_at), 'MMM dd, HH:mm:ss')}</TableCell>
                <TableCell>
                  <IconButton size="small" onClick={() => handleViewDetails(action)} color="primary">
                    <Visibility />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={detailsOpen} onClose={() => setDetailsOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Action Details - #{selectedAction?.id}</DialogTitle>
        <DialogContent>
          {selectedAction && (
            <Box>
              {rollbackResult && (
                <Alert severity={rollbackResult.includes('success') ? 'success' : 'error'} sx={{ mb: 2 }}>
                  {rollbackResult}
                </Alert>
              )}
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Template: {selectedAction.template_name}
              </Typography>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Status: {selectedAction.status}
              </Typography>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Risk Score: {selectedAction.risk_score}
              </Typography>
              <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>Parameters:</Typography>
              <Paper sx={{ p: 2, bgcolor: '#f5f5f5' }}>
                <pre>{JSON.stringify(selectedAction.parameters || {}, null, 2)}</pre>
              </Paper>
              {selectedAction.execution_result && (
                <>
                  <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>Execution Result:</Typography>
                  <Paper sx={{ p: 2, bgcolor: '#f5f5f5' }}>
                    <pre>{JSON.stringify(selectedAction.execution_result, null, 2)}</pre>
                  </Paper>
                </>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          {selectedAction?.can_rollback && selectedAction.status === 'completed' && (
            <Button startIcon={<Undo />} onClick={handleRollback} color="warning">
              Rollback Action
            </Button>
          )}
          <Button onClick={() => setDetailsOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
