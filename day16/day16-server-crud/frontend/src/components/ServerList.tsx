import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  AppBar,
  Toolbar,
  Container,
  TextField,
  Grid,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Pagination,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { serverApi, Server, ServerCreate } from '../services/api';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import SearchIcon from '@mui/icons-material/Search';

const ServerList: React.FC = () => {
  const [servers, setServers] = useState<Server[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newServer, setNewServer] = useState<ServerCreate>({
    name: '',
    hostname: '',
    ip_address: '',
    server_type: '',
    environment: '',
    region: '',
    tenant_id: 'default',
  });
  
  const navigate = useNavigate();

  useEffect(() => {
    fetchServers();
  }, [page, search, statusFilter]);

  const fetchServers = async () => {
    setLoading(true);
    try {
      const params = {
        skip: (page - 1) * 10,
        limit: 10,
        ...(search && { search }),
        ...(statusFilter && { status: statusFilter }),
      };
      const response = await serverApi.list(params);
      setServers(response.servers);
      setTotal(response.total);
    } catch (error) {
      console.error('Failed to fetch servers:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateServer = async () => {
    try {
      await serverApi.create(newServer);
      setCreateDialogOpen(false);
      setNewServer({
        name: '',
        hostname: '',
        ip_address: '',
        server_type: '',
        environment: '',
        region: '',
        tenant_id: 'default',
      });
      fetchServers();
    } catch (error) {
      console.error('Failed to create server:', error);
    }
  };

  const handleDeleteServer = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this server?')) {
      try {
        await serverApi.delete(id);
        fetchServers();
      } catch (error) {
        console.error('Failed to delete server:', error);
      }
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

  return (
    <Box sx={{ flexGrow: 1, bgcolor: '#f8f9fa', minHeight: '100vh' }}>
      <AppBar position="static" sx={{ bgcolor: '#1976d2' }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Server Management
          </Typography>
          <Button
            color="inherit"
            onClick={() => navigate('/')}
          >
            Dashboard
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h5" component="div">
                Servers ({total})
              </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setCreateDialogOpen(true)}
              >
                Add Server
              </Button>
            </Box>

            {/* Filters */}
            <Grid container spacing={3} sx={{ mb: 3 }}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Search servers..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  InputProps={{
                    startAdornment: <SearchIcon sx={{ mr: 1, color: 'action.active' }} />,
                  }}
                />
              </Grid>
              <Grid item xs={12} md={3}>
                <FormControl fullWidth>
                  <InputLabel>Status Filter</InputLabel>
                  <Select
                    value={statusFilter}
                    label="Status Filter"
                    onChange={(e) => setStatusFilter(e.target.value)}
                  >
                    <MenuItem value="">All</MenuItem>
                    <MenuItem value="active">Active</MenuItem>
                    <MenuItem value="maintenance">Maintenance</MenuItem>
                    <MenuItem value="decommissioned">Decommissioned</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>

            {/* Server Table */}
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow sx={{ bgcolor: '#f5f5f5' }}>
                    <TableCell><strong>Name</strong></TableCell>
                    <TableCell><strong>Hostname</strong></TableCell>
                    <TableCell><strong>IP Address</strong></TableCell>
                    <TableCell><strong>Status</strong></TableCell>
                    <TableCell><strong>Environment</strong></TableCell>
                    <TableCell><strong>Region</strong></TableCell>
                    <TableCell><strong>Actions</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {servers.map((server) => (
                    <TableRow key={server.id} hover>
                      <TableCell>
                        <Typography variant="subtitle2">{server.name}</Typography>
                        <Typography variant="caption" color="textSecondary">
                          {server.server_type}
                        </Typography>
                      </TableCell>
                      <TableCell>{server.hostname}</TableCell>
                      <TableCell>{server.ip_address}</TableCell>
                      <TableCell>
                        <Chip
                          label={server.status.toUpperCase()}
                          color={getStatusColor(server.status) as any}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>{server.environment || '-'}</TableCell>
                      <TableCell>{server.region || '-'}</TableCell>
                      <TableCell>
                        <IconButton
                          size="small"
                          onClick={() => navigate(`/servers/${server.id}`)}
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={() => handleDeleteServer(server.id)}
                          color="error"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>

            {/* Pagination */}
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
              <Pagination
                count={Math.ceil(total / 10)}
                page={page}
                onChange={(e, value) => setPage(value)}
                color="primary"
              />
            </Box>
          </CardContent>
        </Card>
      </Container>

      {/* Create Server Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Add New Server</DialogTitle>
        <DialogContent>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Server Name"
                value={newServer.name}
                onChange={(e) => setNewServer({ ...newServer, name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Hostname"
                value={newServer.hostname}
                onChange={(e) => setNewServer({ ...newServer, hostname: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="IP Address"
                value={newServer.ip_address}
                onChange={(e) => setNewServer({ ...newServer, ip_address: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Server Type"
                value={newServer.server_type}
                onChange={(e) => setNewServer({ ...newServer, server_type: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Environment"
                value={newServer.environment}
                onChange={(e) => setNewServer({ ...newServer, environment: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Region"
                value={newServer.region}
                onChange={(e) => setNewServer({ ...newServer, region: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateServer} variant="contained">Create Server</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ServerList;
