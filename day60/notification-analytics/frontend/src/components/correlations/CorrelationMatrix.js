import React, { useState, useEffect } from 'react';
import { Paper, Typography, Box, FormControl, InputLabel, Select, MenuItem, Chip } from '@mui/material';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

function CorrelationMatrix({ metrics, selectedMetric }) {
  const [correlations, setCorrelations] = useState([]);

  useEffect(() => {
    fetchCorrelations();
    const interval = setInterval(fetchCorrelations, 60000);
    return () => clearInterval(interval);
  }, [selectedMetric]);

  const fetchCorrelations = async () => {
    try {
      const response = await axios.get(`${API_BASE}/correlations/${selectedMetric}`);
      setCorrelations(response.data.correlated_metrics);
    } catch (error) {
      console.error('Error fetching correlations:', error);
    }
  };

  return (
    <Paper sx={{ p: 3, borderRadius: 2, border: '1px solid #e5e7eb' }}>
      <Typography variant="h6" gutterBottom sx={{ color: '#1f2937', fontWeight: 600 }}>
        Metric Correlations for {selectedMetric}
      </Typography>
      
      {correlations.length === 0 ? (
        <Typography sx={{ color: '#6b7280', mt: 2 }}>No significant correlations found</Typography>
      ) : (
        <Box sx={{ mt: 2 }}>
          {correlations.map((corr, idx) => (
            <Box 
              key={idx} 
              sx={{ 
                mb: 2, 
                p: 2.5, 
                border: '1px solid #e5e7eb', 
                borderRadius: 2, 
                bgcolor: '#ffffff',
                transition: 'all 0.2s',
                '&:hover': {
                  bgcolor: '#f9fafb',
                  borderColor: '#d1d5db',
                  boxShadow: 1
                }
              }}
            >
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="subtitle1" sx={{ color: '#1f2937', fontWeight: 600 }}>{corr.metric}</Typography>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Chip 
                    label={`${(corr.correlation * 100).toFixed(0)}%`} 
                    sx={{
                      bgcolor: corr.correlation > 0 ? '#10b981' : '#ef4444',
                      color: 'white',
                      fontWeight: 600,
                      '&:hover': {
                        bgcolor: corr.correlation > 0 ? '#059669' : '#dc2626'
                      }
                    }}
                    size="small" 
                  />
                  <Chip 
                    label={corr.strength} 
                    variant="outlined" 
                    size="small"
                    sx={{ 
                      borderColor: '#d1d5db', 
                      color: '#6b7280',
                      fontWeight: 500
                    }}
                  />
                </Box>
              </Box>
              <Box sx={{ mt: 1.5, height: 10, bgcolor: '#e5e7eb', borderRadius: 2, overflow: 'hidden' }}>
                <Box 
                  sx={{ 
                    height: '100%', 
                    width: `${Math.abs(corr.correlation) * 100}%`, 
                    bgcolor: corr.correlation > 0 ? '#10b981' : '#ef4444',
                    borderRadius: 2,
                    transition: 'width 0.3s ease'
                  }} 
                />
              </Box>
            </Box>
          ))}
        </Box>
      )}
    </Paper>
  );
}

export default CorrelationMatrix;

