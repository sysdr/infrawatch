import React, { useState, useEffect } from 'react';
import {
  Box, Paper, Typography, Grid, Button, TextField, Card, 
  CardContent, CardActions, Chip, Alert
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { templateAPI } from '../../services/api';

export default function TemplateManager() {
  const [templates, setTemplates] = useState([]);
  const [templateName, setTemplateName] = useState('');
  const [templateDesc, setTemplateDesc] = useState('');
  const [message, setMessage] = useState(null);

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const res = await templateAPI.listTemplates();
      setTemplates(res.data);
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to load templates' });
    }
  };

  const handleCreateTemplate = async () => {
    if (!templateName) {
      setMessage({ type: 'error', text: 'Template name required' });
      return;
    }

    try {
      await templateAPI.createTemplate({
        name: templateName,
        description: templateDesc,
        query_config: {
          metrics: ['cpu_usage', 'memory_usage', 'error_rate'],
          aggregations: { cpu_usage: 'mean', memory_usage: 'max' }
        },
        layout_config: {
          title: templateName,
          sections: [
            { title: 'Metrics Overview', type: 'table', data_source: 'metrics' },
            { title: 'Trends', type: 'chart', data_source: 'metrics' }
          ]
        }
      });

      setMessage({ type: 'success', text: 'Template created' });
      setTemplateName('');
      setTemplateDesc('');
      await loadTemplates();
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to create template' });
    }
  };

  return (
    <Box>
      {message && (
        <Alert severity={message.type} onClose={() => setMessage(null)} sx={{ mb: 2 }}>
          {message.text}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={5}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Create Template</Typography>
            
            <TextField
              fullWidth
              label="Template Name"
              value={templateName}
              onChange={(e) => setTemplateName(e.target.value)}
              margin="normal"
            />
            
            <TextField
              fullWidth
              label="Description"
              value={templateDesc}
              onChange={(e) => setTemplateDesc(e.target.value)}
              margin="normal"
              multiline
              rows={3}
            />
            
            <Button
              fullWidth
              variant="contained"
              startIcon={<AddIcon />}
              onClick={handleCreateTemplate}
              sx={{ mt: 2 }}
            >
              Create Template
            </Button>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={7}>
          <Typography variant="h6" gutterBottom>Available Templates</Typography>
          
          <Grid container spacing={2}>
            {templates.map(template => (
              <Grid item xs={12} key={template.id}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                      <div>
                        <Typography variant="h6">{template.name}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          {template.description || 'No description'}
                        </Typography>
                        <Box sx={{ mt: 1 }}>
                          <Chip label={`Version ${template.version}`} size="small" sx={{ mr: 1 }} />
                          <Chip 
                            label={`${template.query_config.metrics?.length || 0} metrics`} 
                            size="small" 
                            variant="outlined"
                          />
                        </Box>
                      </div>
                    </Box>
                  </CardContent>
                  <CardActions>
                    <Button size="small">Edit</Button>
                    <Button size="small">Clone</Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Grid>
      </Grid>
    </Box>
  );
}
