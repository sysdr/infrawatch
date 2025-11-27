import React, { useEffect, useState } from 'react';
import { Box, Typography, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Dialog, DialogTitle, DialogContent, DialogActions, TextField } from '@mui/material';
import { Add } from '@mui/icons-material';
import { templateApi } from '../services/api';

export default function Templates() {
  const [templates, setTemplates] = useState([]);
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState({ name: '', description: '', content: '' });

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const response = await templateApi.getAll();
      setTemplates(response.data);
    } catch (error) {
      console.error('Failed to load templates:', error);
    }
  };

  const handleCreate = async () => {
    try {
      await templateApi.create(formData);
      setOpen(false);
      setFormData({ name: '', description: '', content: '' });
      loadTemplates();
    } catch (error) {
      console.error('Failed to create template:', error);
    }
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Templates</Typography>
        <Button 
          variant="contained" 
          startIcon={<Add />} 
          onClick={(e) => {
            e.currentTarget.blur();
            setOpen(true);
          }}
        >
          New Template
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Format</TableCell>
              <TableCell>Version</TableCell>
              <TableCell>Variables</TableCell>
              <TableCell>Created</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {templates.map((template) => (
              <TableRow key={template.id}>
                <TableCell>{template.name}</TableCell>
                <TableCell>{template.description}</TableCell>
                <TableCell>{template.format}</TableCell>
                <TableCell>v{template.version}</TableCell>
                <TableCell>{template.variables.join(', ')}</TableCell>
                <TableCell>{new Date(template.created_at).toLocaleDateString()}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog 
        open={open} 
        onClose={() => setOpen(false)} 
        maxWidth="md" 
        fullWidth
        disableEnforceFocus={false}
        disableAutoFocus={false}
      >
        <DialogTitle>Create Template</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            margin="normal"
          />
          <TextField
            fullWidth
            multiline
            rows={10}
            label="Template Content"
            value={formData.content}
            onChange={(e) => setFormData({ ...formData, content: e.target.value })}
            margin="normal"
            placeholder="<h1>{{ title }}</h1>"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button onClick={handleCreate} variant="contained">Create</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
