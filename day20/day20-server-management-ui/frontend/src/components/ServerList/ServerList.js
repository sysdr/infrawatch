import React, { useState, useMemo } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TableSortLabel,
  TablePagination,
  Checkbox,
  Chip,
  IconButton,
  Menu,
  MenuItem,
  TextField,
  Box,
  FormControl,
  InputLabel,
  Select,
  Tooltip,
  CircularProgress,
} from '@mui/material';
import {
  MoreVert as MoreVertIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  CheckCircle as HealthyIcon,
  Warning as WarningIcon,
  Error as CriticalIcon,
  RadioButtonUnchecked as OfflineIcon,
  Build as MaintenanceIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

import ServerForm from '../ServerForm/ServerForm';
import { serverAPI } from '../../services/api';

const statusIcons = {
  healthy: <HealthyIcon sx={{ color: 'success.main', fontSize: 20 }} />,
  warning: <WarningIcon sx={{ color: 'warning.main', fontSize: 20 }} />,
  critical: <CriticalIcon sx={{ color: 'error.main', fontSize: 20 }} />,
  offline: <OfflineIcon sx={{ color: 'text.disabled', fontSize: 20 }} />,
  maintenance: <MaintenanceIcon sx={{ color: 'primary.main', fontSize: 20 }} />,
};

const ServerList = ({
  servers,
  loading,
  selectedServers,
  onSelectionChange,
  onServerUpdate,
  onServerDelete,
  filters,
  onFiltersChange,
}) => {
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedServer, setSelectedServer] = useState(null);
  const [editingServer, setEditingServer] = useState(null);
  const [sortBy, setSortBy] = useState('name');
  const [sortOrder, setSortOrder] = useState('asc');

  const handleMenuOpen = (event, server) => {
    setAnchorEl(event.currentTarget);
    setSelectedServer(server);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedServer(null);
  };

  const handleSelectAll = (event) => {
    if (event.target.checked) {
      onSelectionChange(servers.map(server => server.id));
    } else {
      onSelectionChange([]);
    }
  };

  const handleSelectOne = (serverId) => {
    if (selectedServers.includes(serverId)) {
      onSelectionChange(selectedServers.filter(id => id !== serverId));
    } else {
      onSelectionChange([...selectedServers, serverId]);
    }
  };

  const handleSort = (column) => {
    const isAsc = sortBy === column && sortOrder === 'asc';
    setSortOrder(isAsc ? 'desc' : 'asc');
    setSortBy(column);
  };

  const handleEdit = () => {
    setEditingServer(selectedServer);
    handleMenuClose();
  };

  const handleView = () => {
    navigate(`/servers/${selectedServer.id}`);
    handleMenuClose();
  };

  const handleDelete = async () => {
    if (window.confirm(`Are you sure you want to delete ${selectedServer.name}?`)) {
      try {
        await serverAPI.deleteServer(selectedServer.id);
        onServerDelete(selectedServer.id);
      } catch (error) {
        console.error('Error deleting server:', error);
      }
    }
    handleMenuClose();
  };

  const sortedServers = useMemo(() => {
    return [...servers].sort((a, b) => {
      const aValue = a[sortBy];
      const bValue = b[sortBy];
      
      if (sortOrder === 'asc') {
        return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      } else {
        return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
      }
    });
  }, [servers, sortBy, sortOrder]);

  const formatUptime = (seconds) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    if (days > 0) {
      return `${days}d ${hours}h`;
    }
    return `${hours}h`;
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height={400}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Filters */}
      <Box sx={{ p: 2, borderBottom: '1px solid #e0e0e0' }}>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <TextField
            size="small"
            placeholder="Search servers..."
            value={filters.search}
            onChange={(e) => onFiltersChange({ ...filters, search: e.target.value })}
            sx={{ minWidth: 200 }}
          />
          
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Status</InputLabel>
            <Select
              value={filters.status}
              onChange={(e) => onFiltersChange({ ...filters, status: e.target.value })}
              label="Status"
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="healthy">Healthy</MenuItem>
              <MenuItem value="warning">Warning</MenuItem>
              <MenuItem value="critical">Critical</MenuItem>
              <MenuItem value="offline">Offline</MenuItem>
              <MenuItem value="maintenance">Maintenance</MenuItem>
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Type</InputLabel>
            <Select
              value={filters.serverType}
              onChange={(e) => onFiltersChange({ ...filters, serverType: e.target.value })}
              label="Type"
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="web">Web</MenuItem>
              <MenuItem value="database">Database</MenuItem>
              <MenuItem value="cache">Cache</MenuItem>
              <MenuItem value="queue">Queue</MenuItem>
              <MenuItem value="load_balancer">Load Balancer</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </Box>

      {/* Table */}
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell padding="checkbox">
                <Checkbox
                  indeterminate={selectedServers.length > 0 && selectedServers.length < servers.length}
                  checked={servers.length > 0 && selectedServers.length === servers.length}
                  onChange={handleSelectAll}
                />
              </TableCell>
              
              <TableCell>Status</TableCell>
              
              <TableCell>
                <TableSortLabel
                  active={sortBy === 'name'}
                  direction={sortBy === 'name' ? sortOrder : 'asc'}
                  onClick={() => handleSort('name')}
                >
                  Name
                </TableSortLabel>
              </TableCell>
              
              <TableCell>
                <TableSortLabel
                  active={sortBy === 'server_type'}
                  direction={sortBy === 'server_type' ? sortOrder : 'asc'}
                  onClick={() => handleSort('server_type')}
                >
                  Type
                </TableSortLabel>
              </TableCell>
              
              <TableCell>IP Address</TableCell>
              <TableCell>CPU</TableCell>
              <TableCell>Memory</TableCell>
              <TableCell>Uptime</TableCell>
              <TableCell>Tags</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          
          <TableBody>
            {sortedServers.map((server) => (
              <TableRow
                key={server.id}
                hover
                selected={selectedServers.includes(server.id)}
              >
                <TableCell padding="checkbox">
                  <Checkbox
                    checked={selectedServers.includes(server.id)}
                    onChange={() => handleSelectOne(server.id)}
                  />
                </TableCell>
                
                <TableCell>
                  <Tooltip title={server.status}>
                    {statusIcons[server.status]}
                  </Tooltip>
                </TableCell>
                
                <TableCell>
                  <Box>
                    <Box sx={{ fontWeight: 500 }}>{server.name}</Box>
                    <Box sx={{ fontSize: '0.875rem', color: 'text.secondary' }}>
                      {server.hostname}
                    </Box>
                  </Box>
                </TableCell>
                
                <TableCell>
                  <Chip
                    label={server.server_type}
                    size="small"
                    variant="outlined"
                    sx={{ textTransform: 'capitalize' }}
                  />
                </TableCell>
                
                <TableCell>{server.ip_address}:{server.port}</TableCell>
                
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Box sx={{ 
                      width: 40, 
                      height: 4, 
                      bgcolor: 'grey.200', 
                      borderRadius: 2,
                      position: 'relative'
                    }}>
                      <Box sx={{ 
                        width: `${server.cpu_usage}%`, 
                        height: '100%',
                        bgcolor: server.cpu_usage > 80 ? 'error.main' : 
                                server.cpu_usage > 60 ? 'warning.main' : 'success.main',
                        borderRadius: 2
                      }} />
                    </Box>
                    <Box sx={{ fontSize: '0.875rem', minWidth: 35 }}>
                      {Math.round(server.cpu_usage)}%
                    </Box>
                  </Box>
                </TableCell>
                
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Box sx={{ 
                      width: 40, 
                      height: 4, 
                      bgcolor: 'grey.200', 
                      borderRadius: 2,
                      position: 'relative'
                    }}>
                      <Box sx={{ 
                        width: `${server.memory_usage}%`, 
                        height: '100%',
                        bgcolor: server.memory_usage > 80 ? 'error.main' : 
                                server.memory_usage > 60 ? 'warning.main' : 'success.main',
                        borderRadius: 2
                      }} />
                    </Box>
                    <Box sx={{ fontSize: '0.875rem', minWidth: 35 }}>
                      {Math.round(server.memory_usage)}%
                    </Box>
                  </Box>
                </TableCell>
                
                <TableCell>
                  {formatUptime(server.uptime)}
                </TableCell>
                
                <TableCell>
                  <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                    {server.tags.slice(0, 2).map((tag) => (
                      <Chip
                        key={tag}
                        label={tag}
                        size="small"
                        variant="outlined"
                        sx={{ fontSize: '0.75rem', height: 20 }}
                      />
                    ))}
                    {server.tags.length > 2 && (
                      <Chip
                        label={`+${server.tags.length - 2}`}
                        size="small"
                        variant="outlined"
                        sx={{ fontSize: '0.75rem', height: 20 }}
                      />
                    )}
                  </Box>
                </TableCell>
                
                <TableCell align="center">
                  <IconButton
                    onClick={(event) => handleMenuOpen(event, server)}
                    size="small"
                  >
                    <MoreVertIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Table Pagination */}
      <TablePagination
        component="div"
        count={servers.length}
        page={filters.page - 1}
        onPageChange={(event, newPage) => 
          onFiltersChange({ ...filters, page: newPage + 1 })
        }
        rowsPerPage={filters.pageSize}
        onRowsPerPageChange={(event) =>
          onFiltersChange({ ...filters, pageSize: parseInt(event.target.value, 10), page: 1 })
        }
      />

      {/* Context Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleView}>
          <ViewIcon sx={{ mr: 1 }} />
          View Details
        </MenuItem>
        <MenuItem onClick={handleEdit}>
          <EditIcon sx={{ mr: 1 }} />
          Edit
        </MenuItem>
        <MenuItem onClick={handleDelete} sx={{ color: 'error.main' }}>
          <DeleteIcon sx={{ mr: 1 }} />
          Delete
        </MenuItem>
      </Menu>

      {/* Edit Form */}
      {editingServer && (
        <ServerForm
          open={Boolean(editingServer)}
          server={editingServer}
          onClose={() => setEditingServer(null)}
          onServerUpdated={(updated) => {
            onServerUpdate(updated);
            setEditingServer(null);
          }}
        />
      )}
    </Box>
  );
};

export default ServerList;
