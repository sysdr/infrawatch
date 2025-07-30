import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  AppBar,
  Toolbar,
  Container,
  Grid,
  TextField,
  Chip,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Divider,
} from '@mui/material';
import { useNavigate, useParams } from 'react-router-dom';
import { serverApi, Server, ServerUpdate } from '../services/api';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import SaveIcon from '@mui/icons-material/Save';

const ServerDetail: React.FC = () => {
  const [server, setServer] = useState<Server | null>(null);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [editMode, setEditMode] = useState(false);
  const [editData, setEditData] = useState<ServerUpdate>({});
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  useEffect(() => {
    if (id) {
      fetchServer(parseInt(id));
      fetchAuditLogs(parseInt(id));
    }
  }, [id]);

  const fetchServer = async (serverId: number) => {
    try {
      const response = await serverApi.get(serverId);
      setServer(response);
      setEditData({
        name: response.name,
        hostname: response.hostname,
        ip_address: response.ip_address,
        status: response.status,
        server_type: response.server_type,
        environment: response.environment,
        region: response.region,
      });
    } catch (error) {
      console.error('Failed to fetch server:', error);
    }
  };

  const fetchAuditLogs = async (serverId: number) => {
    try {
      const response = await serverApi.getAuditLogs(serverId);
      setAuditLogs(response);
    } catch (error) {
      console.error('Failed to fetch audit logs:', error);
    }
  };

  const handleSave = async () => {
    if (!server) return;
    
    try {
      const updatedServer = await serverApi.update(server.id, editData);
      setServer(updatedServer);
      setEditMode(false);
      fetchAuditLogs(server.id); // Refresh audit logs
    } catch (error) {
      console.error('Failed to update server:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'maintenance': return 'warning';
      case 'decommissioned': return 'error';
      default: return 'default';
    }
  };

  if (!server) {
    return <Typography>Loading...</Typography>;
  }

  return (
    <Box sx={{ flexGrow: 1, bgcolor: '#f8f9fa', minHeight: '100vh' }}>
      <AppBar position="static" sx={{ bgcolor: '#1976d2' }}>
        <Toolbar>
          <Button
            color="inherit"
            startIcon={<ArrowBackIcon />}
            onClick={() => navigate('/servers')}
            sx={{ mr: 2 }}
          >
            Back
          </Button>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Server Details: {server.name}
          </Typography>
          {editMode ? (
            <Button
              color="inherit"
              startIcon={<SaveIcon />}
              onClick={handleSave}
            >
              Save Changes
            </Button>
          ) : (
            <Button
              color="inherit"
              onClick={() => setEditMode(true)}
            >
              Edit Server
            </Button>
          )}
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Grid container spacing={3}>
          {/* Server Details */}
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Server Information
                </Typography>
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Server Name"
                      value={editMode ? (editData.name || '') : server.name}
                      onChange={(e) => editMode && setEditData({ ...editData, name: e.target.value })}
                      disabled={!editMode}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Hostname"
                      value={editMode ? (editData.hostname || '') : server.hostname}
                      onChange={(e) => editMode && setEditData({ ...editData, hostname: e.target.value })}
                      disabled={!editMode}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="IP Address"
                      value={editMode ? (editData.ip_address || '') : server.ip_address}
                      onChange={(e) => editMode && setEditData({ ...editData, ip_address: e.target.value })}
                      disabled={!editMode}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Status"
                      select
                      SelectProps={{ native: true }}
                      value={editMode ? (editData.status || '') : server.status}
                      onChange={(e) => editMode && setEditData({ ...editData, status: e.target.value })}
                      disabled={!editMode}
                    >
                      <option value="active">Active</option>
                      <option value="maintenance">Maintenance</option>
                      <option value="decommissioned">Decommissioned</option>
                    </TextField>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Server Type"
                      value={editMode ? (editData.server_type || '') : server.server_type || ''}
                      onChange={(e) => editMode && setEditData({ ...editData, server_type: e.target.value })}
                      disabled={!editMode}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Environment"
                      value={editMode ? (editData.environment || '') : server.environment || ''}
                      onChange={(e) => editMode && setEditData({ ...editData, environment: e.target.value })}
                      disabled={!editMode}
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Server Status */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Status Overview
                </Typography>
                <Box sx={{ mb: 2 }}>
                  <Chip
                    label={server.status.toUpperCase()}
                    color={getStatusColor(server.status) as any}
                    sx={{ mb: 1 }}
                  />
                </Box>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Created: {new Date(server.created_at).toLocaleDateString()}
                </Typography>
                {server.updated_at && (
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    Updated: {new Date(server.updated_at).toLocaleDateString()}
                  </Typography>
                )}
                <Typography variant="body2" color="textSecondary">
                  Version: {server.version}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Audit Logs */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Audit Trail
                </Typography>
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow sx={{ bgcolor: '#f5f5f5' }}>
                        <TableCell><strong>Action</strong></TableCell>
                        <TableCell><strong>User</strong></TableCell>
                        <TableCell><strong>Timestamp</strong></TableCell>
                        <TableCell><strong>Changes</strong></TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {auditLogs.map((log) => (
                        <TableRow key={log.id}>
                          <TableCell>
                            <Chip
                              label={log.action.toUpperCase()}
                              size="small"
                              color={log.action === 'create' ? 'success' : 
                                     log.action === 'update' ? 'warning' : 'error'}
                            />
                          </TableCell>
                          <TableCell>{log.user_id}</TableCell>
                          <TableCell>
                            {new Date(log.timestamp).toLocaleString()}
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" component="pre">
                              {JSON.stringify(log.changes, null, 2)}
                            </Typography>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default ServerDetail;
