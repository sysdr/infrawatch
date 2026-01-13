import React, { useState, useEffect } from 'react';
import {
  Paper,
  Typography,
  Box,
  List,
  ListItem,
  ListItemText,
  Chip,
  LinearProgress,
  Tabs,
  Tab,
} from '@mui/material';
import { CheckCircle, Cancel } from '@mui/icons-material';
import { securityAPI } from '../services/api';

const ComplianceView = () => {
  const [checks, setChecks] = useState([]);
  const [activeFramework, setActiveFramework] = useState('CIS');
  const [frameworks] = useState(['CIS', 'PCI_DSS', 'SOC2', 'GDPR']);

  useEffect(() => {
    loadCompliance();
  }, [activeFramework]);

  const loadCompliance = async () => {
    try {
      const response = await securityAPI.getComplianceResults(activeFramework);
      setChecks(response.data.checks.filter(c => c.framework === activeFramework));
    } catch (error) {
      console.error('Failed to load compliance:', error);
    }
  };

  const calculateScore = () => {
    if (checks.length === 0) return 0;
    const passed = checks.filter(c => c.status === 'passed').length;
    return Math.round((passed / checks.length) * 100);
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
        Compliance Status
      </Typography>

      <Tabs
        value={activeFramework}
        onChange={(e, newValue) => setActiveFramework(newValue)}
        sx={{ mb: 3 }}
      >
        {frameworks.map(fw => (
          <Tab key={fw} label={fw} value={fw} />
        ))}
      </Tabs>

      <Box sx={{ mb: 3 }}>
        <Box display="flex" justifyContent="space-between" mb={1}>
          <Typography variant="body2">Compliance Score</Typography>
          <Typography variant="body2" fontWeight="600">
            {calculateScore()}%
          </Typography>
        </Box>
        <LinearProgress
          variant="determinate"
          value={calculateScore()}
          sx={{ height: 8, borderRadius: 4 }}
          color={calculateScore() >= 90 ? 'success' : calculateScore() >= 70 ? 'warning' : 'error'}
        />
      </Box>

      <List>
        {checks.slice(0, 10).map((check) => (
          <ListItem
            key={check.id}
            sx={{
              border: '1px solid #e0e0e0',
              borderRadius: 1,
              mb: 1,
              bgcolor: check.status === 'passed' ? '#f1f8f4' : '#fef6f6'
            }}
          >
            <Box sx={{ mr: 2 }}>
              {check.status === 'passed' ? (
                <CheckCircle color="success" />
              ) : (
                <Cancel color="error" />
              )}
            </Box>
            <ListItemText
              primary={
                <Box display="flex" alignItems="center" gap={1}>
                  <Typography variant="body1" fontWeight="500">
                    {check.control_id}
                  </Typography>
                  <Chip
                    label={check.severity}
                    size="small"
                    color={check.severity === 'CRITICAL' ? 'error' : 'warning'}
                  />
                </Box>
              }
              secondary={check.control_name}
            />
          </ListItem>
        ))}
      </List>
    </Paper>
  );
};

export default ComplianceView;
