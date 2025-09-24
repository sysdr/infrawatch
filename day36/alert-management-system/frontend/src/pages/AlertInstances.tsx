import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Button,
  IconButton
} from '@mui/material';
import { CheckCircle as CheckIcon } from '@mui/icons-material';
import { alertService } from '../services/alertService';
import { format } from 'date-fns';

interface AlertInstance {
  id: number;
  status: string;
  current_value: number;
  threshold_value: number;
  triggered_at: string;
  acknowledged_at?: string;
  message?: string;
  rule?: {
    name: string;
    severity: string;
    metric_name: string;
  };
}

const AlertInstances: React.FC = () => {
  const [alerts, setAlerts] = useState<AlertInstance[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadActiveAlerts();
  }, []);

  const loadActiveAlerts = async () => {
    try {
      const data = await alertService.getActiveAlerts();
      setAlerts(data);
    } catch (error) {
      console.error('Failed to load active alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAcknowledge = async (instanceId: number) => {
    try {
      await alertService.acknowledgeAlert(instanceId);
      loadActiveAlerts();
    } catch (error) {
      console.error('Failed to acknowledge alert:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'firing': return 'error';
      case 'pending': return 'warning';
      case 'acknowledged': return 'info';
      case 'resolved': return 'success';
      default: return 'default';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'error';
      case 'warning': return 'warning';
      case 'info': return 'info';
      default: return 'default';
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Active Alerts
      </Typography>

      <Card>
        <CardContent>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Alert Rule</TableCell>
                  <TableCell>Metric</TableCell>
                  <TableCell>Current Value</TableCell>
                  <TableCell>Threshold</TableCell>
                  <TableCell>Severity</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Triggered At</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {alerts.map((alert) => (
                  <TableRow key={alert.id}>
                    <TableCell>{alert.rule?.name || 'Unknown'}</TableCell>
                    <TableCell>{alert.rule?.metric_name || 'Unknown'}</TableCell>
                    <TableCell>{alert.current_value}</TableCell>
                    <TableCell>{alert.threshold_value}</TableCell>
                    <TableCell>
                      <Chip
                        label={alert.rule?.severity || 'unknown'}
                        color={getSeverityColor(alert.rule?.severity || '') as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={alert.status}
                        color={getStatusColor(alert.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {format(new Date(alert.triggered_at), 'MMM dd, yyyy HH:mm')}
                    </TableCell>
                    <TableCell>
                      {alert.status !== 'acknowledged' && alert.status !== 'resolved' && (
                        <IconButton
                          size="small"
                          onClick={() => handleAcknowledge(alert.id)}
                          color="primary"
                        >
                          <CheckIcon />
                        </IconButton>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          {alerts.length === 0 && !loading && (
            <Box textAlign="center" py={4}>
              <Typography variant="body1" color="textSecondary">
                No active alerts found
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default AlertInstances;
