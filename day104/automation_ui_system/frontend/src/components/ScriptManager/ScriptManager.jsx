import React, { useState, useEffect } from 'react';
import { Box, Paper, Button, TextField, Dialog, DialogTitle, DialogContent, DialogActions, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, IconButton, Select, MenuItem, FormControl, InputLabel, Chip } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import CodeIcon from '@mui/icons-material/Code';
import { scriptApi } from '../../services/api';
import { toast } from 'react-toastify';

const ScriptManager = () => {
  const [scripts, setScripts] = useState([]);
  const [showDialog, setShowDialog] = useState(false);
  const [editingScript, setEditingScript] = useState(null);
  const [formData, setFormData] = useState({ name: '', description: '', script_type: 'python', content: '' });

  useEffect(() => { loadScripts(); }, []);

  const loadScripts = async () => {
    try {
      const res = await scriptApi.getAll();
      setScripts(res.data.scripts || []);
    } catch (e) { toast.error('Failed to load scripts'); }
  };

  const handleOpenDialog = (script = null) => {
    if (script) {
      setEditingScript(script);
      setFormData({ name: script.name, description: script.description || '', script_type: script.script_type, content: script.content || '' });
    } else {
      setEditingScript(null);
      setFormData({ name: '', description: '', script_type: 'python', content: '' });
    }
    setShowDialog(true);
  };

  const handleSave = async () => {
    try {
      if (editingScript) {
        await scriptApi.update(editingScript.id, formData);
        toast.success('Script updated');
      } else {
        await scriptApi.create(formData);
        toast.success('Script created');
      }
      loadScripts();
      setShowDialog(false);
    } catch (e) { toast.error('Failed to save script'); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this script?')) return;
    try {
      await scriptApi.delete(id);
      toast.success('Script deleted');
      loadScripts();
    } catch (e) { toast.error('Failed to delete'); }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <h2>Script Management</h2>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => handleOpenDialog()}>New Script</Button>
      </Box>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell><TableCell>Type</TableCell><TableCell>Description</TableCell><TableCell>Version</TableCell><TableCell>Status</TableCell><TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {scripts.map((s) => (
              <TableRow key={s.id}>
                <TableCell><Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}><CodeIcon fontSize="small" />{s.name}</Box></TableCell>
                <TableCell><Chip label={s.script_type} size="small" /></TableCell>
                <TableCell>{s.description}</TableCell>
                <TableCell>v{s.version}</TableCell>
                <TableCell><Chip label={s.is_active ? 'Active' : 'Inactive'} color={s.is_active ? 'success' : 'default'} size="small" /></TableCell>
                <TableCell>
                  <IconButton onClick={() => handleOpenDialog(s)} size="small"><EditIcon /></IconButton>
                  <IconButton onClick={() => handleDelete(s.id)} size="small" color="error"><DeleteIcon /></IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <Dialog open={showDialog} onClose={() => setShowDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>{editingScript ? 'Edit Script' : 'New Script'}</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 2 }}>
            <TextField label="Script Name" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} fullWidth />
            <TextField label="Description" value={formData.description} onChange={(e) => setFormData({ ...formData, description: e.target.value })} fullWidth multiline rows={2} />
            <FormControl fullWidth>
              <InputLabel>Script Type</InputLabel>
              <Select value={formData.script_type} onChange={(e) => setFormData({ ...formData, script_type: e.target.value })} label="Script Type">
                <MenuItem value="python">Python</MenuItem><MenuItem value="bash">Bash</MenuItem><MenuItem value="javascript">JavaScript</MenuItem>
              </Select>
            </FormControl>
            <TextField label="Script Content" value={formData.content} onChange={(e) => setFormData({ ...formData, content: e.target.value })} fullWidth multiline rows={10} sx={{ fontFamily: 'monospace' }} />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowDialog(false)}>Cancel</Button>
          <Button onClick={handleSave} variant="contained">{editingScript ? 'Update' : 'Create'}</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ScriptManager;
