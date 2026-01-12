import React, { useState, useEffect } from 'react';
import {
  Paper, Typography, Box, Button, TextField, Switch, FormControlLabel,
  Alert, CircularProgress, Card, CardContent, Grid
} from '@mui/material';
import SyncIcon from '@mui/icons-material/Sync';
import axios from 'axios';

function LDAPSync() {
  const [configs, setConfigs] = useState([]);
  const [syncing, setSyncing] = useState(false);
  const [result, setResult] = useState(null);
  const [newConfig, setNewConfig] = useState({
    name: 'Primary LDAP',
    server: 'ldap://localhost:389',
    base_dn: 'dc=example,dc=com',
    bind_dn: 'cn=admin,dc=example,dc=com',
    bind_password: 'admin',
    user_filter: '(objectClass=inetOrgPerson)',
    sync_interval_minutes: 30
  });

  useEffect(() => {
    fetchConfigs();
  }, []);

  const fetchConfigs = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/v1/ldap/configs');
      setConfigs(response.data);
    } catch (error) {
      console.error('Error fetching configs:', error);
    }
  };

  const handleSync = async (configId) => {
    setSyncing(true);
    setResult(null);
    try {
      const response = await axios.post(`http://localhost:8000/api/v1/ldap/sync/${configId}`);
      setResult({ type: 'success', data: response.data });
      fetchConfigs();
    } catch (error) {
      setResult({ type: 'error', message: error.message });
    } finally {
      setSyncing(false);
    }
  };

  const handleCreateConfig = async () => {
    try {
      await axios.post('http://localhost:8000/api/v1/ldap/configs', newConfig);
      fetchConfigs();
      setResult({ type: 'success', message: 'LDAP configuration created successfully' });
    } catch (error) {
      setResult({ type: 'error', message: error.message });
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>LDAP Directory Sync</Typography>

      {result && (
        <Alert severity={result.type} sx={{ mb: 3 }} onClose={() => setResult(null)}>
          {result.message || JSON.stringify(result.data)}
        </Alert>
      )}

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>LDAP Configurations</Typography>
        <Grid container spacing={2}>
          {configs.map((config) => (
            <Grid item xs={12} md={6} key={config.id}>
              <Card>
                <CardContent>
                  <Typography variant="h6">{config.name}</Typography>
                  <Typography variant="body2" color="textSecondary">Server: {config.server}</Typography>
                  <Typography variant="body2" color="textSecondary">Base DN: {config.base_dn}</Typography>
                  <Typography variant="body2" color="textSecondary">
                    Last Sync: {config.last_sync ? new Date(config.last_sync).toLocaleString() : 'Never'}
                  </Typography>
                  <Box mt={2}>
                    <Button
                      variant="contained"
                      startIcon={syncing ? <CircularProgress size={20} /> : <SyncIcon />}
                      onClick={() => handleSync(config.id)}
                      disabled={syncing}
                      fullWidth
                    >
                      {syncing ? 'Syncing...' : 'Sync Now'}
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Paper>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>Add New LDAP Configuration</Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Name"
              value={newConfig.name}
              onChange={(e) => setNewConfig({ ...newConfig, name: e.target.value })}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Server"
              value={newConfig.server}
              onChange={(e) => setNewConfig({ ...newConfig, server: e.target.value })}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Base DN"
              value={newConfig.base_dn}
              onChange={(e) => setNewConfig({ ...newConfig, base_dn: e.target.value })}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Bind DN"
              value={newConfig.bind_dn}
              onChange={(e) => setNewConfig({ ...newConfig, bind_dn: e.target.value })}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              type="password"
              label="Bind Password"
              value={newConfig.bind_password}
              onChange={(e) => setNewConfig({ ...newConfig, bind_password: e.target.value })}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="User Filter"
              value={newConfig.user_filter}
              onChange={(e) => setNewConfig({ ...newConfig, user_filter: e.target.value })}
            />
          </Grid>
          <Grid item xs={12}>
            <Button variant="contained" onClick={handleCreateConfig}>
              Create Configuration
            </Button>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
}

export default LDAPSync;
