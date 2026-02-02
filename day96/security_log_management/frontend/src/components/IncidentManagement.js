import React, { useState, useEffect } from 'react';
import { Paper, Typography, Box, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip, Button, Dialog, DialogTitle, DialogContent, DialogActions, TextField } from '@mui/material';
import { incidentApi } from '../services/api';

function IncidentManagement() {
  const [incidents, setIncidents] = useState([]);
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [resolutionNotes, setResolutionNotes] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadIncidents();
  }, []);

  const loadIncidents = async () => {
    try {
      const response = await incidentApi.getIncidents({ limit: 50 });
      setIncidents(response.data.incidents || []);
      setLoading(false);
    } catch (error) {
      console.error('Error loading incidents:', error);
      setLoading(false);
    }
  };

  const handleViewIncident = (incident) => {
    setSelectedIncident(incident);
    setDialogOpen(true);
  };

  const handleResolveIncident = async () => {
    if (!selectedIncident) return;

    try {
      await incidentApi.updateIncident(selectedIncident.incident_id, {
        status: 'resolved',
        resolution_notes: resolutionNotes
      });
      setDialogOpen(false);
      setResolutionNotes('');
      loadIncidents();
    } catch (error) {
      console.error('Error resolving incident:', error);
    }
  };

  const getSeverityColor = (severity) => {
    const colors = {
      critical: 'error',
      high: 'warning',
      medium: 'info',
      low: 'default'
    };
    return colors[severity] || 'default';
  };

  if (loading) {
    return <Typography>Loading incidents...</Typography>;
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Incident Management
      </Typography>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Incident ID</TableCell>
              <TableCell>Title</TableCell>
              <TableCell>Severity</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {incidents.map((incident) => (
              <TableRow key={incident.id}>
                <TableCell>{incident.incident_id}</TableCell>
                <TableCell>{incident.title}</TableCell>
                <TableCell>
                  <Chip
                    label={incident.severity}
                    color={getSeverityColor(incident.severity)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={incident.status}
                    color={incident.status === 'resolved' ? 'success' : 'default'}
                    size="small"
                  />
                </TableCell>
                <TableCell>{incident.incident_type}</TableCell>
                <TableCell>{new Date(incident.created_at).toLocaleString()}</TableCell>
                <TableCell>
                  <Button
                    size="small"
                    onClick={() => handleViewIncident(incident)}
                  >
                    View
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Incident Details Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Incident Details</DialogTitle>
        <DialogContent>
          {selectedIncident && (
            <Box>
              <Typography variant="subtitle1" gutterBottom>
                <strong>ID:</strong> {selectedIncident.incident_id}
              </Typography>
              <Typography variant="subtitle1" gutterBottom>
                <strong>Title:</strong> {selectedIncident.title}
              </Typography>
              <Typography variant="body1" gutterBottom>
                <strong>Description:</strong> {selectedIncident.description}
              </Typography>
              <Typography variant="body2" gutterBottom>
                <strong>Detection Method:</strong> {selectedIncident.detection_method}
              </Typography>
              <Typography variant="body2" gutterBottom>
                <strong>Confidence Score:</strong> {selectedIncident.confidence_score}%
              </Typography>
              
              {selectedIncident.status !== 'resolved' && (
                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  label="Resolution Notes"
                  value={resolutionNotes}
                  onChange={(e) => setResolutionNotes(e.target.value)}
                  sx={{ mt: 2 }}
                />
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Close</Button>
          {selectedIncident && selectedIncident.status !== 'resolved' && (
            <Button onClick={handleResolveIncident} variant="contained" color="primary">
              Resolve Incident
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default IncidentManagement;
