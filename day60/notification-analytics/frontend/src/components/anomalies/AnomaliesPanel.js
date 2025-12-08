import React, { useState, useEffect } from 'react';
import { Paper, Typography, Box, Chip, Alert, List, ListItem, ListItemText } from '@mui/material';
import { Warning, Error, Info } from '@mui/icons-material';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

function AnomaliesPanel({ metrics }) {
  const [anomalies, setAnomalies] = useState([]);

  useEffect(() => {
    fetchAnomalies();
    const interval = setInterval(fetchAnomalies, 15000);
    return () => clearInterval(interval);
  }, []);

  const fetchAnomalies = async () => {
    try {
      const response = await axios.get(`${API_BASE}/anomalies?hours=24`);
      setAnomalies(response.data.anomalies);
    } catch (error) {
      console.error('Error fetching anomalies:', error);
    }
  };

  const getSeverityColor = (severity) => {
    const colors = { critical: 'error', high: 'warning', medium: 'info', low: 'success' };
    return colors[severity] || 'default';
  };

  const getSeverityIcon = (severity) => {
    if (severity === 'critical' || severity === 'high') return <Error />;
    if (severity === 'medium') return <Warning />;
    return <Info />;
  };

  return (
    <Paper sx={{ p: 3, borderRadius: 2, border: '1px solid #e5e7eb' }}>
      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1, color: '#1f2937', fontWeight: 600 }}>
        <Warning sx={{ color: '#f59e0b' }} />
        Detected Anomalies ({anomalies.length})
      </Typography>
      
      {anomalies.length === 0 ? (
        <Alert severity="success" sx={{ mt: 2, borderRadius: 2, bgcolor: '#ecfdf5', color: '#065f46', border: '1px solid #10b981' }}>
          No anomalies detected in the last 24 hours
        </Alert>
      ) : (
        <List>
          {anomalies.slice(-20).reverse().map((anomaly, idx) => (
            <ListItem key={idx} sx={{ 
              border: '1px solid #e5e7eb', 
              borderRadius: 2, 
              mb: 1.5, 
              bgcolor: '#ffffff',
              transition: 'all 0.2s',
              '&:hover': {
                bgcolor: '#f9fafb',
                borderColor: '#d1d5db',
                boxShadow: 1
              }
            }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                {getSeverityIcon(anomaly.severity)}
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                      <Typography variant="subtitle1" sx={{ color: '#1f2937', fontWeight: 600 }}>{anomaly.metric_name}</Typography>
                      <Chip 
                        label={anomaly.severity} 
                        color={getSeverityColor(anomaly.severity)} 
                        size="small"
                        sx={{ fontWeight: 500 }}
                      />
                      <Chip 
                        label={anomaly.type} 
                        size="small" 
                        variant="outlined"
                        sx={{ borderColor: '#d1d5db', color: '#6b7280' }}
                      />
                    </Box>
                  }
                  secondary={
                    <>
                      <Typography variant="body2" sx={{ color: '#4b5563', mt: 0.5 }}>
                        Value: {anomaly.actual?.toFixed(2)} | Expected: {anomaly.expected?.toFixed(2)} | Z-Score: {anomaly.z_score?.toFixed(2)}
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#9ca3af', display: 'block', mt: 0.5 }}>
                        Confidence: {(anomaly.confidence * 100).toFixed(0)}% | {new Date(anomaly.detected_at).toLocaleString()}
                      </Typography>
                    </>
                  }
                />
              </Box>
            </ListItem>
          ))}
        </List>
      )}
    </Paper>
  );
}

export default AnomaliesPanel;
