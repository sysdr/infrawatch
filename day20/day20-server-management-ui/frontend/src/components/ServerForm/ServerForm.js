import React, { useState, useEffect } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, TextField, Button, MenuItem } from '@mui/material';
import { serverAPI } from '../../services/api';

const ServerForm = ({ open, onClose, onServerCreated, server }) => {
  const [form, setForm] = useState({
    name: '', hostname: '', ip_address: '', port: 22, server_type: 'web', tags: []
  });

  useEffect(() => {
    if (server) {
      setForm({
        name: server.name,
        hostname: server.hostname,
        ip_address: server.ip_address,
        port: server.port,
        server_type: server.server_type,
        tags: server.tags || [],
      });
    }
  }, [server]);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async () => {
    if (server) {
      const updated = await serverAPI.updateServer(server.id, form);
      onServerCreated?.(updated);
    } else {
      const created = await serverAPI.createServer(form);
      onServerCreated?.(created);
    }
    onClose?.();
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>{server ? 'Edit Server' : 'Add Server'}</DialogTitle>
      <DialogContent sx={{ display: 'grid', gap: 2, pt: 2 }}>
        <TextField label="Name" name="name" value={form.name} onChange={handleChange} required />
        <TextField label="Hostname" name="hostname" value={form.hostname} onChange={handleChange} required />
        <TextField label="IP Address" name="ip_address" value={form.ip_address} onChange={handleChange} required />
        <TextField label="Port" name="port" type="number" value={form.port} onChange={handleChange} />
        <TextField select label="Type" name="server_type" value={form.server_type} onChange={handleChange}>
          <MenuItem value="web">Web</MenuItem>
          <MenuItem value="database">Database</MenuItem>
          <MenuItem value="cache">Cache</MenuItem>
          <MenuItem value="queue">Queue</MenuItem>
          <MenuItem value="load_balancer">Load Balancer</MenuItem>
        </TextField>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button variant="contained" onClick={handleSubmit}>{server ? 'Save' : 'Create'}</Button>
      </DialogActions>
    </Dialog>
  );
};

export default ServerForm;
