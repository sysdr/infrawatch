import React from 'react';
import { Box, Chip, Tooltip } from '@mui/material';

const CorrelationMatrix = ({ correlations }) => {
  if (!correlations || correlations.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height={300}>
        <div style={{ textAlign: 'center', color: '#999' }}>
          <p>No correlations detected yet</p>
          <p style={{ fontSize: '0.9em' }}>Generate sample data and detect correlations to see the matrix</p>
        </div>
      </Box>
    );
  }

  const getColor = (coefficient) => {
    const abs = Math.abs(coefficient);
    if (abs >= 0.9) return coefficient > 0 ? '#2e7d32' : '#c62828';
    if (abs >= 0.7) return coefficient > 0 ? '#66bb6a' : '#ef5350';
    if (abs >= 0.5) return coefficient > 0 ? '#81c784' : '#e57373';
    return coefficient > 0 ? '#a5d6a7' : '#ef9a9a';
  };

  const getStateColor = (state) => {
    switch(state) {
      case 'active': return 'success';
      case 'candidate': return 'warning';
      case 'validating': return 'info';
      case 'decaying': return 'default';
      default: return 'default';
    }
  };

  return (
    <Box sx={{ overflowY: 'auto', maxHeight: 350 }}>
      {correlations.slice(0, 20).map((corr, index) => (
        <Tooltip 
          key={index}
          title={`${corr.correlation_type} | p-value: ${corr.p_value.toFixed(4)} | lag: ${corr.lag_seconds}s`}
        >
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              p: 1.5,
              mb: 1,
              borderRadius: 2,
              background: 'rgba(255,255,255,0.7)',
              border: '1px solid #e0e0e0',
              transition: 'all 0.2s',
              '&:hover': {
                transform: 'translateX(5px)',
                boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
              }
            }}
          >
            <Box sx={{ flex: 1 }}>
              <div style={{ fontSize: '0.9em', fontWeight: 500 }}>
                {corr.metric_a.name} ↔ {corr.metric_b.name}
              </div>
              <div style={{ fontSize: '0.75em', color: '#666', marginTop: 4 }}>
                <Chip 
                  label={corr.state} 
                  size="small" 
                  color={getStateColor(corr.state)}
                  sx={{ mr: 1 }}
                />
                {corr.lag_seconds !== 0 && (
                  <span>Lag: {corr.lag_seconds}s</span>
                )}
              </div>
            </Box>
            <Box
              sx={{
                minWidth: 80,
                textAlign: 'center',
                fontWeight: 'bold',
                fontSize: '1.1em',
                color: getColor(corr.coefficient),
                background: getColor(corr.coefficient) + '20',
                padding: '8px 12px',
                borderRadius: 1,
              }}
            >
              {corr.coefficient.toFixed(3)}
            </Box>
          </Box>
        </Tooltip>
      ))}
    </Box>
  );
};

export default CorrelationMatrix;
