import { useState, useEffect } from 'react';
import {
  Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Button, Box, Typography, Dialog, DialogTitle, DialogContent, DialogActions, TextField
} from '@mui/material';
import { CheckCircle, Cancel } from '@mui/icons-material';
import { format } from 'date-fns';
import { api } from '../services/api';
import type { RemediationAction } from '../types';

export default function ApprovalQueue() {
  const [pendingActions, setPendingActions] = useState<RemediationAction[]>([]);
  const [selectedAction, setSelectedAction] = useState<RemediationAction | null>(null);
  const [approvalOpen, setApprovalOpen] = useState(false);
  const [comments, setComments] = useState('');

  useEffect(() => {
    loadPendingActions();
    const interval = setInterval(loadPendingActions, 3000);
    return () => clearInterval(interval);
  }, []);

  const loadPendingActions = async () => {
    try {
      const { data } = await api.getActions('pending');
      setPendingActions(data);
    } catch (e) {
      console.error('Failed to load pending actions:', e);
    }
  };

  const handleApprove = async () => {
    if (!selectedAction) return;
    try {
      await api.approveAction(selectedAction.id, 'admin', comments);
      setApprovalOpen(false);
      setComments('');
      loadPendingActions();
    } catch (e) {
      console.error('Failed to approve action:', e);
    }
  };

  const handleReject = async () => {
    if (!selectedAction) return;
    try {
      await api.rejectAction(selectedAction.id);
      setApprovalOpen(false);
      loadPendingActions();
    } catch (e) {
      console.error('Failed to reject action:', e);
    }
  };

  const getRiskColor = (score: number) => {
    if (score < 30) return '#4caf50';
    if (score < 60) return '#ff9800';
    return '#f44336';
  };

  return (
    <>
      {pendingActions.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" color="textSecondary">No pending approvals</Typography>
        </Paper>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead sx={{ bgcolor: '#fff3e0' }}>
              <TableRow>
                <TableCell><strong>ID</strong></TableCell>
                <TableCell><strong>Template</strong></TableCell>
                <TableCell><strong>Incident</strong></TableCell>
                <TableCell><strong>Risk Score</strong></TableCell>
                <TableCell><strong>Blast Radius</strong></TableCell>
                <TableCell><strong>Created</strong></TableCell>
                <TableCell><strong>Actions</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {pendingActions.map((action) => (
                <TableRow key={action.id} hover>
                  <TableCell>{action.id}</TableCell>
                  <TableCell>{action.template_name}</TableCell>
                  <TableCell><Typography variant="body2" sx={{ fontFamily: 'monospace' }}>{action.incident_id}</Typography></TableCell>
                  <TableCell><Box component="span" sx={{ bgcolor: getRiskColor(action.risk_score), color: 'white', px: 1, py: 0.5, borderRadius: 1 }}>{action.risk_score}</Box></TableCell>
                  <TableCell>{action.blast_radius}</TableCell>
                  <TableCell>{format(new Date(action.created_at), 'MMM dd, HH:mm:ss')}</TableCell>
                  <TableCell>
                    <Button size="small" variant="contained" color="success" startIcon={<CheckCircle />}
                      onClick={() => { setSelectedAction(action); setApprovalOpen(true); }}>Review</Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <Dialog open={approvalOpen} onClose={() => setApprovalOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Review Action #{selectedAction?.id}</DialogTitle>
        <DialogContent>
          {selectedAction && (
            <Box>
              <Typography variant="body1" gutterBottom><strong>Template:</strong> {selectedAction.template_name}</Typography>
              <Typography variant="body1" gutterBottom><strong>Risk Score:</strong> {selectedAction.risk_score}</Typography>
              <Typography variant="body1" gutterBottom><strong>Blast Radius:</strong> {selectedAction.blast_radius} resources</Typography>
              <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>Parameters:</Typography>
              <Paper sx={{ p: 2, bgcolor: '#f5f5f5' }}><pre>{JSON.stringify(selectedAction.parameters || {}, null, 2)}</pre></Paper>
              <TextField label="Approval Comments" multiline rows={3} fullWidth value={comments} onChange={(e) => setComments(e.target.value)} sx={{ mt: 2 }} />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleReject} color="error" startIcon={<Cancel />}>Reject</Button>
          <Button onClick={handleApprove} color="success" variant="contained" startIcon={<CheckCircle />}>Approve</Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
