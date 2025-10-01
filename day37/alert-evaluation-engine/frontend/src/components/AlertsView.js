import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  Button,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  CheckCircle as ResolveIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { apiService } from '../services/apiService';

function AlertsView() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 15000); // Refresh every 15s
    return () => clearInterval(interval);
  }, []);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const data = await apiService.getActiveAlerts();
      setAlerts(data);
    } catch (error) {
      console.error('Failed to fetch alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'CRITICAL': return 'error';
      case 'WARNING': return 'warning';
      case 'INFO': return 'info';
      default: return 'default';
    }
  };

  const getStateColor = (state) => {
    switch (state) {
      case 'FIRING': return 'error';
      case 'PENDING': return 'warning';
      case 'RESOLVED': return 'success';
      default: return 'default';
    }
  };

  const formatDuration = (startTime) => {
    const now = new Date();
    const start = new Date(startTime);
    const diffMs = now - start;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 60) {
      return `${diffMins}m`;
    } else {
      const hours = Math.floor(diffMins / 60);
      const mins = diffMins % 60;
      return `${hours}h ${mins}m`;
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Active Alerts</Typography>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={fetchAlerts}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>

      {alerts.length === 0 ? (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 6 }}>
            <ResolveIcon sx={{ fontSize: 64, color: 'success.main', mb: 2 }} />
            <Typography variant="h5" color="success.main">
              No Active Alerts
            </Typography>
            <Typography color="text.secondary">
              All systems are running normally
            </Typography>
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={2}>
          {alerts.map((alert) => (
            <Grid item xs={12} key={alert.id}>
              <Card sx={{ 
                borderLeft: 4, 
                borderColor: alert.severity === 'CRITICAL' ? 'error.main' : 
                           alert.severity === 'WARNING' ? 'warning.main' : 'info.main'
              }}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <Box sx={{ flex: 1 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                        <Typography variant="h6">
                          {alert.rule_name}
                        </Typography>
                        <Chip 
                          label={alert.severity}
                          color={getSeverityColor(alert.severity)}
                          size="small"
                        />
                        <Chip 
                          label={alert.state}
                          color={getStateColor(alert.state)}
                          variant="outlined"
                          size="small"
                        />
                      </Box>
                      
                      <Typography variant="body1" sx={{ mb: 2 }}>
                        {alert.message}
                      </Typography>
                      
                      <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                        {Object.entries(alert.labels).map(([key, value]) => (
                          <Chip 
                            key={key}
                            label={`${key}: ${value}`}
                            variant="outlined"
                            size="small"
                          />
                        ))}
                      </Box>
                      
                      <Typography variant="caption" color="text.secondary">
                        Started: {formatDuration(alert.starts_at)} ago • 
                        Value: {typeof alert.value === 'number' ? alert.value.toFixed(2) : alert.value}
                      </Typography>
                    </Box>
                    
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Tooltip title="Acknowledge">
                        <IconButton>
                          <ResolveIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Details">
                        <IconButton>
                          <InfoIcon />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
}

export default AlertsView;
