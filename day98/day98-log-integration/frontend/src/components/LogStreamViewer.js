import React, { useState, useEffect, useRef } from 'react';
import {
  Paper,
  Typography,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  List,
  ListItem,
  ListItemText,
  Button,
  CircularProgress
} from '@mui/material';
import { format } from 'date-fns';
import api from '../services/api';

const LOG_LEVELS = ['DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL'];
const SERVICES = ['all', 'auth-api', 'user-service', 'payment-service', 'notification-service'];
const POLL_INTERVAL_MS = 2500;

const SAMPLE_LOGS = [
  { level: 'INFO', service: 'auth-api', message: 'User login successful', metadata: { user_id: 'demo' } },
  { level: 'WARN', service: 'notification-service', message: 'Rate limit approaching', metadata: {} },
  { level: 'ERROR', service: 'notification-service', message: 'Delivery failed for batch', metadata: { retry: true } },
  { level: 'INFO', service: 'user-service', message: 'Profile updated', metadata: {} },
  { level: 'ERROR', service: 'auth-api', message: 'authentication failed for user', metadata: { user_id: 'test', ip: '192.168.1.1' } },
];

const DEMO_LOGS = (() => {
  const now = new Date();
  return [
    { id: 'demo-1', timestamp: new Date(now - 5000).toISOString(), level: 'INFO', service: 'auth-api', message: 'User login successful', metadata: {} },
    { id: 'demo-2', timestamp: new Date(now - 4500).toISOString(), level: 'WARN', service: 'notification-service', message: 'Rate limit approaching', metadata: {} },
    { id: 'demo-3', timestamp: new Date(now - 4000).toISOString(), level: 'ERROR', service: 'payment-service', message: 'Payment gateway timeout', metadata: {} },
    { id: 'demo-4', timestamp: new Date(now - 3500).toISOString(), level: 'INFO', service: 'user-service', message: 'Profile updated successfully', metadata: {} },
    { id: 'demo-5', timestamp: new Date(now - 3000).toISOString(), level: 'DEBUG', service: 'auth-api', message: 'Token validation completed', metadata: {} },
    { id: 'demo-6', timestamp: new Date(now - 2500).toISOString(), level: 'ERROR', service: 'auth-api', message: 'Authentication failed for user', metadata: { ip: '192.168.1.1' } },
    { id: 'demo-7', timestamp: new Date(now - 2000).toISOString(), level: 'INFO', service: 'notification-service', message: 'Email sent successfully', metadata: {} },
    { id: 'demo-8', timestamp: new Date(now - 1500).toISOString(), level: 'WARN', service: 'user-service', message: 'Cache miss for session', metadata: {} },
    { id: 'demo-9', timestamp: new Date(now - 1000).toISOString(), level: 'INFO', service: 'payment-service', message: 'Transaction completed', metadata: {} },
    { id: 'demo-10', timestamp: new Date(now - 500).toISOString(), level: 'ERROR', service: 'notification-service', message: 'Delivery failed for batch', metadata: { retry: true } },
  ];
})();

function LogStreamViewer() {
  const [logs, setLogs] = useState(DEMO_LOGS);
  const [selectedLevel, setSelectedLevel] = useState('all');
  const [selectedService, setSelectedService] = useState('all');
  const [generating, setGenerating] = useState(false);
  const logsEndRef = useRef(null);

  const loadRecentLogs = async () => {
    try {
      const params = { limit: 100 };
      if (selectedService !== 'all') params.service = selectedService;
      if (selectedLevel !== 'all') params.level = selectedLevel;
      const res = await api.get('/api/logs/search', { params, timeout: 5000 });
      const recentLogs = res.data?.logs || [];
      if (recentLogs.length > 0) setLogs(recentLogs);
    } catch (e) {}
  };

  const generateTestLogs = async () => {
    setGenerating(true);
    try {
      for (const log of SAMPLE_LOGS) {
        await api.post('/api/logs/', log);
      }
      await loadRecentLogs();
    } catch (e) {
      console.error('Failed to generate logs:', e);
    } finally {
      setGenerating(false);
    }
  };

  useEffect(() => {
    loadRecentLogs();
  }, [selectedService, selectedLevel]);

  useEffect(() => {
    const interval = setInterval(loadRecentLogs, POLL_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [selectedService, selectedLevel]);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const clearLogs = () => setLogs(DEMO_LOGS);

  const getLogColor = (level) => ({
    DEBUG: '#9e9e9e', INFO: '#2196f3', WARN: '#ff9800', ERROR: '#f44336', FATAL: '#d32f2f'
  }[level] || '#000');

  return (
    <Box>
      <Paper sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">Log Stream</Typography>
          <Chip label={`${logs.length} logs`} color="success" size="small" />
        </Box>

        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mb: 2, alignItems: 'center' }}>
          <FormControl size="small" sx={{ minWidth: 200 }}>
            <InputLabel>Service</InputLabel>
            <Select value={selectedService} label="Service" onChange={(e) => setSelectedService(e.target.value)}>
              {SERVICES.map(s => <MenuItem key={s} value={s}>{s}</MenuItem>)}
            </Select>
          </FormControl>
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Level</InputLabel>
            <Select value={selectedLevel} label="Level" onChange={(e) => setSelectedLevel(e.target.value)}>
              <MenuItem value="all">All</MenuItem>
              {LOG_LEVELS.map(l => <MenuItem key={l} value={l}>{l}</MenuItem>)}
            </Select>
          </FormControl>
          <Button variant="outlined" onClick={clearLogs}>Clear</Button>
          <Button variant="contained" color="primary" onClick={generateTestLogs} disabled={generating} sx={{ fontWeight: 'bold', bgcolor: '#e65100' }}>
            {generating ? <CircularProgress size={20} sx={{ mr: 1 }} color="inherit" /> : null}
            Generate Test Logs
          </Button>
        </Box>
      </Paper>

      <Paper sx={{ height: 600, overflow: 'auto', bgcolor: '#1e1e1e', p: 2 }}>
        <List dense>
          {logs.map((log, index) => (
            <ListItem key={log.id || index} sx={{ py: 0.5 }}>
              <ListItemText
                primary={
                  <Box sx={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>
                    <span style={{ color: '#9e9e9e' }}>[{log.timestamp ? format(new Date(log.timestamp), 'HH:mm:ss.SSS') : 'N/A'}]</span>
                    {' '}<span style={{ color: getLogColor(log.level), fontWeight: 'bold' }}>{log.level}</span>
                    {' '}<span style={{ color: '#4fc3f7' }}>[{log.service}]</span>
                    {' '}<span style={{ color: '#ffffff' }}>{log.message}</span>
                  </Box>
                }
              />
            </ListItem>
          ))}
          <div ref={logsEndRef} />
        </List>
      </Paper>
    </Box>
  );
}

export default LogStreamViewer;
