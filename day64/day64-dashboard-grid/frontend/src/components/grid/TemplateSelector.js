import React, { useState, useEffect } from 'react';
import { Paper, Typography, List, ListItem, ListItemButton, ListItemText, Button, Box } from '@mui/material';
import { templateAPI } from '../../services/api';

const TemplateSelector = ({ dashboardId, onTemplateApply }) => {
  const [templates, setTemplates] = useState([]);

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const response = await templateAPI.getAll();
      setTemplates(response.data);
    } catch (error) {
      console.error('Failed to load templates:', error);
    }
  };

  const handleApplyTemplate = async (templateId) => {
    try {
      await templateAPI.apply(templateId, dashboardId);
      onTemplateApply();
    } catch (error) {
      console.error('Failed to apply template:', error);
    }
  };

  return (
    <Paper 
      sx={{ 
        p: 2.5, 
        minHeight: '200px',
        borderRadius: 3,
        border: '1px solid #e2e8f0',
        bgcolor: '#ffffff',
      }}
    >
      <Typography 
        variant="h6" 
        gutterBottom
        sx={{ 
          fontWeight: 600,
          color: '#1e293b',
          mb: 2,
        }}
      >
        Templates
      </Typography>
      {templates.length === 0 ? (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          No templates available
        </Typography>
      ) : (
        <List sx={{ py: 0 }}>
          {templates.map((template) => (
            <ListItem key={template.id} disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton 
                onClick={() => handleApplyTemplate(template.id)}
                sx={{
                  borderRadius: 2,
                  '&:hover': {
                    bgcolor: 'rgba(16, 185, 129, 0.08)',
                  },
                }}
              >
                <ListItemText
                  primary={template.name}
                  secondary={template.description}
                  primaryTypographyProps={{
                    fontWeight: 500,
                    fontSize: '0.95rem',
                  }}
                  secondaryTypographyProps={{
                    fontSize: '0.8rem',
                  }}
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      )}
    </Paper>
  );
};

export default TemplateSelector;
