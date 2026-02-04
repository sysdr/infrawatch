import React, { useState, useEffect } from 'react';
import {
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Chip,
  Button,
  List,
  ListItem,
  ListItemText,
  Divider,
  Alert
} from '@mui/material';
import WarningIcon from '@mui/icons-material/Warning';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { format } from 'date-fns';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

function SecurityAlerts() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchAlerts = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/alerts`);
      setAlerts(response.data);
    } catch (error) {
      console.error('Error fetching alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const resolveAlert = async (alertId) => {
    try {
      await axios.post(`${API_BASE_URL}/api/alerts/${alertId}/resolve`);
      fetchAlerts();
    } catch (error) {
      console.error('Error resolving alert:', error);
    }
  };

  const getSeverityColor = (severity) => {
    const colors = {
      HIGH: 'error',
      MEDIUM: 'warning',
      LOW: 'info'
    };
    return colors[severity] || 'default';
  };

  const activeAlerts = alerts.filter(a => !a.resolved);
  const resolvedAlerts = alerts.filter(a => a.resolved);

  return (
    <Box>
      <Paper sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">Security Alerts</Typography>
          <Box>
            <Chip
              icon={<WarningIcon />}
              label={`${activeAlerts.length} Active`}
              color="error"
              sx={{ mr: 1 }}
            />
            <Chip
              icon={<CheckCircleIcon />}
              label={`${resolvedAlerts.length} Resolved`}
              color="success"
            />
          </Box>
        </Box>
      </Paper>

      {activeAlerts.length === 0 && !loading ? (
        <Alert severity="success">
          No active security alerts. System is operating normally.
        </Alert>
      ) : (
        <Box>
          <Typography variant="subtitle1" gutterBottom>Active Alerts</Typography>
          {activeAlerts.map((alert) => (
            <Card key={alert.id} sx={{ mb: 2, borderLeft: 4, borderColor: 'error.main' }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      {alert.title}
                    </Typography>
                    <Chip
                      label={alert.severity}
                      color={getSeverityColor(alert.severity)}
                      size="small"
                      sx={{ mr: 1 }}
                    />
                    <Chip
                      label={alert.alert_type}
                      size="small"
                      variant="outlined"
                    />
                  </Box>
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => resolveAlert(alert.id)}
                  >
                    Resolve
                  </Button>
                </Box>

                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {alert.description}
                </Typography>

                <Divider sx={{ my: 2 }} />

                <Typography variant="subtitle2" gutterBottom>Context:</Typography>
                <List dense>
                  {Object.entries(alert.context).map(([key, value]) => (
                    <ListItem key={key}>
                      <ListItemText
                        primary={`${key}: ${JSON.stringify(value)}`}
                        primaryTypographyProps={{
                          variant: 'body2',
                          sx: { fontFamily: 'monospace' }
                        }}
                      />
                    </ListItem>
                  ))}
                </List>

                <Typography variant="caption" color="text.secondary">
                  Triggered: {format(new Date(alert.triggered_at), 'yyyy-MM-dd HH:mm:ss')}
                  {alert.occurrence_count > 1 && ` (${alert.occurrence_count} occurrences)`}
                </Typography>
              </CardContent>
            </Card>
          ))}
        </Box>
      )}
    </Box>
  );
}

export default SecurityAlerts;
