import React from 'react';
import {
  Box,
  List,
  ListItem,
  ListItemText,
  Chip,
  Typography,
  Divider
} from '@mui/material';
import { Warning, Error as ErrorIcon, Info } from '@mui/icons-material';
import { formatDistanceToNow } from 'date-fns';

function ThreatList({ threats }) {
  const getSeverityIcon = (severity) => {
    if (severity >= 80) return <ErrorIcon color="error" />;
    if (severity >= 60) return <Warning color="warning" />;
    return <Info color="info" />;
  };

  const getSeverityColor = (severity) => {
    if (severity >= 80) return 'error';
    if (severity >= 60) return 'warning';
    return 'info';
  };

  if (!threats || threats.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', py: 5, color: 'text.secondary' }}>
        <Typography>No active threats detected</Typography>
      </Box>
    );
  }

  return (
    <List sx={{ maxHeight: 600, overflow: 'auto' }}>
      {threats.map((threat, index) => (
        <React.Fragment key={threat.threat_id}>
          <ListItem alignItems="flex-start">
            <Box sx={{ width: '100%' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                {getSeverityIcon(threat.severity)}
                <Typography variant="subtitle2" fontWeight="bold">
                  {threat.attack_type?.replace(/_/g, ' ') || 'Unknown Threat'}
                </Typography>
                <Chip
                  label={`Severity: ${threat.severity}`}
                  size="small"
                  color={getSeverityColor(threat.severity)}
                />
              </Box>
              
              <Typography variant="body2" color="text.secondary" gutterBottom>
                User: {threat.user_id || 'Unknown'} | IP: {threat.ip_address || 'N/A'}
              </Typography>
              
              <Typography variant="caption" color="text.secondary">
                Detected {formatDistanceToNow(new Date(threat.detected_at))} ago
              </Typography>
              
              {threat.automated_response && (
                <Chip
                  label="Auto-responded"
                  size="small"
                  color="success"
                  sx={{ mt: 1 }}
                />
              )}
            </Box>
          </ListItem>
          {index < threats.length - 1 && <Divider />}
        </React.Fragment>
      ))}
    </List>
  );
}

export default ThreatList;
