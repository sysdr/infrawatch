import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  Alert
} from '@mui/material';
import { Delete as DeleteIcon, Computer, Phone, Tablet } from '@mui/icons-material';
import axios from 'axios';

const DeviceManagement = ({ userId }) => {
  const [sessions, setSessions] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/api/auth/sessions?user_id=${userId}`);
      setSessions(response.data.sessions);
    } catch (err) {
      setError('Failed to load sessions');
    }
  };

  const revokeSession = async (sessionId) => {
    try {
      await axios.delete(`http://localhost:8000/api/auth/sessions/${sessionId}?user_id=${userId}`);
      fetchSessions();
    } catch (err) {
      setError('Failed to revoke session');
    }
  };

  const getDeviceIcon = (userAgent) => {
    if (userAgent.includes('Mobile')) return <Phone />;
    if (userAgent.includes('Tablet')) return <Tablet />;
    return <Computer />;
  };

  return (
    <Box sx={{ maxWidth: 800, margin: '0 auto', mt: 4 }}>
      <Card>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Active Sessions
          </Typography>

          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

          <List>
            {sessions.map((session) => (
              <ListItem
                key={session.session_id}
                sx={{
                  border: 1,
                  borderColor: 'divider',
                  borderRadius: 1,
                  mb: 2
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', mr: 2 }}>
                  {getDeviceIcon(session.user_agent)}
                </Box>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="subtitle1" component="span">
                        {session.user_agent.split('/')[0]}
                      </Typography>
                      {session.mfa_verified && (
                        <Chip label="MFA Verified" size="small" color="success" />
                      )}
                    </Box>
                  }
                  secondary={
                    <Box component="span">
                      <Box component="span" sx={{ display: 'block' }}>
                        IP: {session.ip_address}
                      </Box>
                      <Box component="span" sx={{ display: 'block' }}>
                        Last active: {new Date(session.last_activity).toLocaleString()}
                      </Box>
                    </Box>
                  }
                />
                <ListItemSecondaryAction>
                  <IconButton
                    edge="end"
                    onClick={() => revokeSession(session.session_id)}
                  >
                    <DeleteIcon />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        </CardContent>
      </Card>
    </Box>
  );
};

export default DeviceManagement;
