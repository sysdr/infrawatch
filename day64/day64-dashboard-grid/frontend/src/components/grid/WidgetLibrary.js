import React from 'react';
import { Paper, Typography, List, ListItem, ListItemButton, ListItemText, Box } from '@mui/material';
import { widgetRegistry } from '../../utils/widgetRegistry';

const WidgetLibrary = ({ onWidgetAdd }) => {
  const widgets = Object.entries(widgetRegistry);

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
        Widget Library
      </Typography>
      {widgets.length === 0 ? (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          No widgets available
        </Typography>
      ) : (
        <List sx={{ py: 0 }}>
          {widgets.map(([type, config]) => (
            <ListItem key={type} disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton 
                onClick={() => onWidgetAdd(type)}
                sx={{
                  borderRadius: 2,
                  '&:hover': {
                    bgcolor: 'rgba(16, 185, 129, 0.08)',
                  },
                }}
              >
                <ListItemText
                  primary={config.name}
                  secondary={config.description}
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

export default WidgetLibrary;
