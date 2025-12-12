import React, { useState, useEffect } from 'react';
import { Paper, Typography, List, ListItem, ListItemText, Chip, Box } from '@mui/material';

const AlertList = ({ config = {} }) => {
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    const severities = ['critical', 'warning', 'info'];
    const messages = [
      'High CPU usage detected',
      'Memory threshold exceeded',
      'Disk space running low',
      'Network latency increased',
      'Database connection timeout',
    ];

    const generateAlerts = () => {
      const newAlerts = Array.from({ length: config.limit || 10 }, (_, i) => ({
        id: i,
        severity: severities[Math.floor(Math.random() * severities.length)],
        message: messages[Math.floor(Math.random() * messages.length)],
        time: new Date().toLocaleTimeString(),
      }));
      setAlerts(newAlerts);
    };

    generateAlerts();
    const interval = setInterval(generateAlerts, 10000);

    return () => clearInterval(interval);
  }, [config.limit]);

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'error';
      case 'warning': return 'warning';
      default: return 'info';
    }
  };

  return (
    <Paper sx={{ height: '100%', p: 2.5, display: 'flex', flexDirection: 'column', bgcolor: 'transparent', boxShadow: 'none' }}>
      <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, color: '#1e293b' }}>
        Recent Alerts
      </Typography>
      <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
        <List dense sx={{ py: 0 }}>
          {alerts.map((alert) => (
            <ListItem key={alert.id} sx={{ px: 0, py: 1, borderRadius: 1, mb: 0.5, '&:hover': { bgcolor: '#f8fafc' } }}>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Chip 
                      label={alert.severity} 
                      size="small" 
                      color={getSeverityColor(alert.severity)}
                      sx={{ fontWeight: 500, fontSize: '0.7rem' }}
                    />
                    <Typography variant="body2" sx={{ fontWeight: 500, color: '#1e293b' }}>
                      {alert.message}
                    </Typography>
                  </Box>
                }
                secondary={
                  <Typography variant="caption" sx={{ color: '#64748b', mt: 0.5 }}>
                    {alert.time}
                  </Typography>
                }
              />
            </ListItem>
          ))}
        </List>
      </Box>
    </Paper>
  );
};

export default AlertList;
