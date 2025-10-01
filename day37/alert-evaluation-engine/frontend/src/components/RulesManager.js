import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  TextField,
  MenuItem,
  DialogActions,
  IconButton,
  Switch,
  FormControlLabel
} from '@mui/material';
import { Add as AddIcon, Edit as EditIcon } from '@mui/icons-material';
import { apiService } from '../services/apiService';

function RulesManager() {
  const [rules, setRules] = useState([]);
  const [open, setOpen] = useState(false);
  const [newRule, setNewRule] = useState({
    name: '',
    description: '',
    metric_name: '',
    rule_type: 'THRESHOLD',
    conditions: { greater_than: 80 },
    severity: 'WARNING',
    evaluation_interval: 30,
    for_duration: 300,
    labels: {},
    annotations: {},
    enabled: true
  });

  useEffect(() => {
    fetchRules();
  }, []);

  const fetchRules = async () => {
    try {
      const data = await apiService.getAlertRules();
      setRules(data);
    } catch (error) {
      console.error('Failed to fetch rules:', error);
    }
  };

  const handleCreateRule = async () => {
    try {
      await apiService.createAlertRule(newRule);
      setOpen(false);
      fetchRules();
      // Reset form
      setNewRule({
        name: '',
        description: '',
        metric_name: '',
        rule_type: 'THRESHOLD',
        conditions: { greater_than: 80 },
        severity: 'WARNING',
        evaluation_interval: 30,
        for_duration: 300,
        labels: {},
        annotations: {},
        enabled: true
      });
    } catch (error) {
      console.error('Failed to create rule:', error);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'CRITICAL': return 'error';
      case 'WARNING': return 'warning';
      case 'INFO': return 'info';
      default: return 'default';
    }
  };

  const getRuleTypeColor = (type) => {
    switch (type) {
      case 'THRESHOLD': return 'primary';
      case 'ANOMALY': return 'secondary';
      case 'COMPOSITE': return 'info';
      default: return 'default';
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Alert Rules</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpen(true)}
        >
          Create Rule
        </Button>
      </Box>

      <Grid container spacing={3}>
        {rules.map((rule) => (
          <Grid item xs={12} md={6} lg={4} key={rule.id}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Typography variant="h6" component="div">
                    {rule.name}
                  </Typography>
                  <IconButton size="small">
                    <EditIcon />
                  </IconButton>
                </Box>
                
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {rule.description}
                </Typography>

                <Box sx={{ mb: 2 }}>
                  <Typography variant="caption" display="block">
                    Metric: {rule.metric_name}
                  </Typography>
                  <Typography variant="caption" display="block">
                    Interval: {rule.evaluation_interval}s
                  </Typography>
                </Box>

                <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                  <Chip 
                    label={rule.rule_type} 
                    color={getRuleTypeColor(rule.rule_type)}
                    size="small"
                  />
                  <Chip 
                    label={rule.severity} 
                    color={getSeverityColor(rule.severity)}
                    size="small"
                  />
                </Box>

                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  {Object.entries(rule.labels).map(([key, value]) => (
                    <Chip 
                      key={key}
                      label={`${key}: ${value}`}
                      variant="outlined"
                      size="small"
                    />
                  ))}
                </Box>

                <FormControlLabel
                  control={<Switch checked={rule.enabled} size="small" id={`switch-${rule.id}`} />}
                  label="Enabled"
                  htmlFor={`switch-${rule.id}`}
                  sx={{ mt: 1 }}
                />
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Create Rule Dialog */}
      <Dialog 
        open={open} 
        onClose={() => setOpen(false)} 
        maxWidth="md" 
        fullWidth
        disableEnforceFocus
        disableAutoFocus
        disableRestoreFocus
        disablePortal
        keepMounted={false}
      >
        <DialogTitle>Create New Alert Rule</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Rule Name"
                value={newRule.name}
                onChange={(e) => setNewRule({...newRule, name: e.target.value})}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Metric Name"
                value={newRule.metric_name}
                onChange={(e) => setNewRule({...newRule, metric_name: e.target.value})}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                multiline
                rows={2}
                value={newRule.description}
                onChange={(e) => setNewRule({...newRule, description: e.target.value})}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                select
                fullWidth
                label="Rule Type"
                value={newRule.rule_type}
                onChange={(e) => setNewRule({...newRule, rule_type: e.target.value})}
              >
                <MenuItem value="THRESHOLD">Threshold</MenuItem>
                <MenuItem value="ANOMALY">Anomaly</MenuItem>
                <MenuItem value="COMPOSITE">Composite</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                select
                fullWidth
                label="Severity"
                value={newRule.severity}
                onChange={(e) => setNewRule({...newRule, severity: e.target.value})}
              >
                <MenuItem value="INFO">Info</MenuItem>
                <MenuItem value="WARNING">Warning</MenuItem>
                <MenuItem value="CRITICAL">Critical</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Evaluation Interval (s)"
                type="number"
                value={newRule.evaluation_interval}
                onChange={(e) => setNewRule({...newRule, evaluation_interval: parseInt(e.target.value)})}
              />
            </Grid>
            {newRule.rule_type === 'THRESHOLD' && (
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Threshold Value"
                  type="number"
                  value={newRule.conditions.greater_than || ''}
                  onChange={(e) => setNewRule({
                    ...newRule, 
                    conditions: { greater_than: parseFloat(e.target.value) }
                  })}
                />
              </Grid>
            )}
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateRule} variant="contained">
            Create Rule
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default RulesManager;
