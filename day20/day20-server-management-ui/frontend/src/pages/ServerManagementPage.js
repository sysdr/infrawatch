import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';

import ServerList from '../components/ServerList/ServerList';
import ServerForm from '../components/ServerForm/ServerForm';
import BulkActions from '../components/BulkActions/BulkActions';
import ServerMetrics from '../components/common/ServerMetrics';
import { serverAPI } from '../services/api';
import { useWebSocket } from '../hooks/useWebSocket';

const ServerManagementPage = () => {
  const [servers, setServers] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [selectedServers, setSelectedServers] = useState([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    search: '',
    status: '',
    serverType: '',
    page: 1,
    pageSize: 50,
  });

  const { lastMessage } = useWebSocket();

  useEffect(() => {
    loadServers();
    loadMetrics();
  }, [filters]);

  useEffect(() => {
    // Handle WebSocket messages
    if (lastMessage) {
      try {
        const data = JSON.parse(lastMessage.data);
        
        if (data.type === 'status_update') {
          updateServerStatus(data.server_id, data.new_status);
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    }
  }, [lastMessage]);

  const loadServers = async () => {
    try {
      setLoading(true);
      const response = await serverAPI.getServers(filters);
      setServers(response.servers);
    } catch (error) {
      console.error('Error loading servers:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadMetrics = async () => {
    try {
      const metricsData = await serverAPI.getMetrics();
      setMetrics(metricsData);
    } catch (error) {
      console.error('Error loading metrics:', error);
    }
  };

  const updateServerStatus = (serverId, newStatus) => {
    setServers(prev => prev.map(server => 
      server.id === serverId 
        ? { ...server, status: newStatus }
        : server
    ));
  };

  const handleServerCreated = (newServer) => {
    setServers(prev => [...prev, newServer]);
    setShowAddForm(false);
    loadMetrics(); // Refresh metrics
  };

  const handleServerUpdated = (updatedServer) => {
    setServers(prev => prev.map(server => 
      server.id === updatedServer.id ? updatedServer : server
    ));
    loadMetrics();
  };

  const handleServerDeleted = (serverId) => {
    setServers(prev => prev.filter(server => server.id !== serverId));
    setSelectedServers(prev => prev.filter(id => id !== serverId));
    loadMetrics();
  };

  const handleBulkAction = async (action, parameters) => {
    try {
      const result = await serverAPI.bulkAction({
        action,
        server_ids: selectedServers,
        parameters,
      });

      // Refresh server list and clear selection
      await loadServers();
      setSelectedServers([]);
      loadMetrics();

      return result;
    } catch (error) {
      console.error('Bulk action failed:', error);
      throw error;
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Server Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setShowAddForm(true)}
          sx={{ bgcolor: 'primary.main' }}
        >
          Add Server
        </Button>
      </Box>

      {/* Server Metrics */}
      {metrics && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12}>
            <ServerMetrics metrics={metrics} />
          </Grid>
        </Grid>
      )}

      {/* Bulk Actions */}
      {selectedServers.length > 0 && (
        <Box sx={{ mb: 2 }}>
          <BulkActions
            selectedCount={selectedServers.length}
            onBulkAction={handleBulkAction}
          />
        </Box>
      )}

      {/* Server List */}
      <Card className="server-table-container">
        <CardContent sx={{ p: 0 }}>
          <ServerList
            servers={servers}
            loading={loading}
            selectedServers={selectedServers}
            onSelectionChange={setSelectedServers}
            onServerUpdate={handleServerUpdated}
            onServerDelete={handleServerDeleted}
            filters={filters}
            onFiltersChange={setFilters}
          />
        </CardContent>
      </Card>

      {/* Add Server Form */}
      <ServerForm
        open={showAddForm}
        onClose={() => setShowAddForm(false)}
        onServerCreated={handleServerCreated}
      />
    </Box>
  );
};

export default ServerManagementPage;
