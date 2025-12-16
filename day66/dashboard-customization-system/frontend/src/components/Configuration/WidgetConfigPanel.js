import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Box
} from '@mui/material';

const WidgetConfigPanel = ({ open, widget, onClose, onSave }) => {
  const [config, setConfig] = useState(widget?.config || {});

  const handleSave = () => {
    onSave({ ...widget, config });
    onClose();
  };

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="sm" 
      fullWidth
      aria-labelledby="widget-config-dialog-title"
    >
      <DialogTitle id="widget-config-dialog-title">Configure Widget</DialogTitle>
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 2 }}>
          <TextField
            label="Widget Title"
            value={config.title || ''}
            onChange={(e) => setConfig({ ...config, title: e.target.value })}
            fullWidth
          />
          
          {widget?.widget_type === 'timeseries' && (
            <>
              <TextField
                label="Metric"
                value={config.metric || ''}
                onChange={(e) => setConfig({ ...config, metric: e.target.value })}
                fullWidth
              />
              <FormControl fullWidth>
                <InputLabel>Aggregation</InputLabel>
                <Select
                  value={config.aggregation || 'avg'}
                  onChange={(e) => setConfig({ ...config, aggregation: e.target.value })}
                >
                  <MenuItem value="avg">Average</MenuItem>
                  <MenuItem value="sum">Sum</MenuItem>
                  <MenuItem value="max">Maximum</MenuItem>
                  <MenuItem value="min">Minimum</MenuItem>
                </Select>
              </FormControl>
            </>
          )}
          
          <TextField
            label="Refresh Interval (seconds)"
            type="number"
            value={(config.refreshInterval || 30000) / 1000}
            onChange={(e) => setConfig({ ...config, refreshInterval: parseInt(e.target.value) * 1000 })}
            fullWidth
          />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSave} variant="contained">Save</Button>
      </DialogActions>
    </Dialog>
  );
};

export default WidgetConfigPanel;
